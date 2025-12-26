"""
APTOS Binary Model Architecture - EfficientNet + CBAM
Reconstructed from checkpoint structure
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import timm


class ChannelAttention(nn.Module):
    """Channel Attention from CBAM"""
    def __init__(self, channels, reduction=16):
        super(ChannelAttention, self).__init__()
        self.avg_pool = nn.AdaptiveAvgPool2d(1)
        self.fc1 = nn.Linear(channels, channels // reduction, bias=False)
        self.relu = nn.ReLU(inplace=True)
        self.fc2 = nn.Linear(channels // reduction, channels, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        b, c, _, _ = x.shape
        y = self.avg_pool(x).view(b, c)
        y = self.fc2(self.relu(self.fc1(y)))
        y = self.sigmoid(y).view(b, c, 1, 1)
        return y


class SpatialAttention(nn.Module):
    """Spatial Attention from CBAM"""
    def __init__(self):
        super(SpatialAttention, self).__init__()
        self.conv = nn.Conv2d(2, 1, kernel_size=7, padding=3, bias=False)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        max_pool = torch.max(x, dim=1, keepdim=True)[0]
        avg_pool = torch.mean(x, dim=1, keepdim=True)
        concat = torch.cat([max_pool, avg_pool], dim=1)
        return self.sigmoid(self.conv(concat))


class CBAM(nn.Module):
    """
    Convolutional Block Attention Module (CBAM)
    Channel attention + Spatial attention
    """
    def __init__(self, channels, reduction=16):
        super(CBAM, self).__init__()
        self.channel_attention = ChannelAttention(channels, reduction)
        self.spatial_attention = SpatialAttention()

    def forward(self, x):
        x = x * self.channel_attention(x)
        x = x * self.spatial_attention(x)
        return x


class APTOSDualBranchModel(nn.Module):
    """
    Dual-branch EfficientNet model with CBAM attention
    Takes vessel map and green channel as separate inputs

    Architecture:
    - Vessel branch: EfficientNet-B3 + CBAM
    - Green branch: EfficientNet-B3 + CBAM
    - Concatenate features
    - MLP classifier
    """
    def __init__(self, num_classes=2):
        super(APTOSDualBranchModel, self).__init__()

        # Create EfficientNet-B4 backbones (1-channel input each)
        self.vessel_backbone = timm.create_model(
            'tf_efficientnet_b4',
            pretrained=False,
            in_chans=1,
            num_classes=0,  # Remove classification head
            global_pool=''   # Remove global pooling
        )

        self.green_backbone = timm.create_model(
            'tf_efficientnet_b4',
            pretrained=False,
            in_chans=1,
            num_classes=0,
            global_pool=''
        )

        # Get feature dimensions (EfficientNet-B4 outputs 1792 channels)
        self.feature_dim = 1792

        # CBAM attention modules
        self.vessel_cbam = CBAM(self.feature_dim, reduction=16)
        self.green_cbam = CBAM(self.feature_dim, reduction=16)

        # Global pooling
        self.global_pool = nn.AdaptiveAvgPool2d(1)

        # Classifier (concatenated features from both branches)
        # Structure matches checkpoint: Linear -> BatchNorm -> Dropout pattern
        self.classifier = nn.Sequential(
            nn.Dropout(0.3),                    # 0
            nn.Linear(self.feature_dim * 2, 512),  # 1
            nn.ReLU(inplace=True),              # 2
            nn.BatchNorm1d(512),                # 3
            nn.Dropout(0.3),                    # 4
            nn.Linear(512, 256),                # 5
            nn.ReLU(inplace=True),              # 6
            nn.BatchNorm1d(256),                # 7
            nn.Dropout(0.2),                    # 8
            nn.Linear(256, num_classes)         # 9
        )

    def forward(self, vessel, green):
        # Vessel branch
        vessel_feat = self.vessel_backbone(vessel)
        vessel_feat = self.vessel_cbam(vessel_feat)
        vessel_feat = self.global_pool(vessel_feat)
        vessel_feat = vessel_feat.flatten(1)

        # Green branch
        green_feat = self.green_backbone(green)
        green_feat = self.green_cbam(green_feat)
        green_feat = self.global_pool(green_feat)
        green_feat = green_feat.flatten(1)

        # Concatenate and classify
        combined = torch.cat([vessel_feat, green_feat], dim=1)
        logits = self.classifier(combined)

        # Return format matching ConvNeXt model (main_logits, aux_logits, features, attn_weights)
        # aux_logits and attn_weights are dummy values for compatibility
        return logits, logits, combined, None


if __name__ == '__main__':
    # Test model
    print("Testing APTOS Dual-Branch Model...")
    model = APTOSDualBranchModel(num_classes=2)

    vessel = torch.randn(2, 1, 288, 288)
    green = torch.randn(2, 1, 288, 288)

    main_logits, aux_logits, features, _ = model(vessel, green)

    print(f"Vessel input: {vessel.shape}")
    print(f"Green input: {green.shape}")
    print(f"Main logits: {main_logits.shape}")
    print(f"Features: {features.shape}")
    print(f"Total parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M")
