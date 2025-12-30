import torch
import torch.nn as nn
import torch.nn.functional as F
import timm


class DualStreamConvNeXtModel(nn.Module):
    def __init__(self, num_classes=2):
        super().__init__()

        self.vessel_backbone = timm.create_model(
            'convnext_large.fb_in22k_ft_in1k_384',
            pretrained=False,  # We load our own trained weights
            num_classes=0,
            in_chans=1,
            drop_path_rate=0.1
        )
        self.green_backbone = timm.create_model(
            'convnext_large.fb_in22k_ft_in1k_384',
            pretrained=False,  # We load our own trained weights
            num_classes=0,
            in_chans=1,
            drop_path_rate=0.1
        )

        embed_dim = self.vessel_backbone.num_features

        self.cross_attention = nn.MultiheadAttention(
            embed_dim, num_heads=16, dropout=0.1, batch_first=True
        )
        self.self_attn_vessel = nn.MultiheadAttention(
            embed_dim, num_heads=16, dropout=0.1, batch_first=True
        )
        self.self_attn_green = nn.MultiheadAttention(
            embed_dim, num_heads=16, dropout=0.1, batch_first=True
        )

        self.norm1 = nn.LayerNorm(embed_dim)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.norm3 = nn.LayerNorm(embed_dim)

        self.fusion = nn.Sequential(
            nn.Linear(embed_dim * 2, embed_dim * 2),
            nn.BatchNorm1d(embed_dim * 2),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(embed_dim * 2, embed_dim),
            nn.BatchNorm1d(embed_dim),
            nn.GELU(),
            nn.Dropout(0.15),
            nn.Linear(embed_dim, embed_dim // 2),
            nn.BatchNorm1d(embed_dim // 2)
        )

        self.classifier = nn.Sequential(
            nn.Linear(embed_dim // 2, 512),
            nn.BatchNorm1d(512),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(512, 384),
            nn.BatchNorm1d(384),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(384, 192),
            nn.BatchNorm1d(192),
            nn.GELU(),
            nn.Dropout(0.05),
            nn.Linear(192, num_classes)
        )

        self.aux_classifier = nn.Linear(embed_dim * 2, num_classes)

    def forward(self, vessel, green):
        vessel_feat = self.vessel_backbone(vessel)
        green_feat = self.green_backbone(green)

        vessel_self, _ = self.self_attn_vessel(
            vessel_feat.unsqueeze(1), vessel_feat.unsqueeze(1), vessel_feat.unsqueeze(1)
        )
        vessel_enhanced = self.norm1(vessel_self.squeeze(1) + vessel_feat)

        green_self, _ = self.self_attn_green(
            green_feat.unsqueeze(1), green_feat.unsqueeze(1), green_feat.unsqueeze(1)
        )
        green_enhanced = self.norm2(green_self.squeeze(1) + green_feat)

        cross_attn, attn_weights = self.cross_attention(
            vessel_enhanced.unsqueeze(1),
            green_enhanced.unsqueeze(1),
            green_enhanced.unsqueeze(1)
        )
        cross_enhanced = self.norm3(cross_attn.squeeze(1) + vessel_enhanced)

        combined = torch.cat([cross_enhanced, green_enhanced], dim=1)
        fused_features = self.fusion(combined)

        main_logits = self.classifier(fused_features)
        aux_logits = self.aux_classifier(combined)

        return main_logits, aux_logits, fused_features, attn_weights


class FocalLoss(nn.Module):
    """Focal Loss for handling class imbalance (included for reference)"""
    def __init__(self, alpha=1, gamma=2.5):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * ce_loss
        return focal_loss.mean()
