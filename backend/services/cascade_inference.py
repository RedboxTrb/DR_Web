import torch
import torch.nn.functional as F


def cascade_classify(vessel_input, green_input, model_manager, stage1_threshold=0.35):
    """
    Perform cascade classification through 4 stages

    Args:
        vessel_input: preprocessed vessel tensor of shape (1, 1, 288, 288)
        green_input: preprocessed green tensor of shape (1, 1, 288, 288)
        model_manager: ModelManager instance with loaded models
        stage1_threshold: DR probability threshold (default 0.35)
                         If P(DR) >= threshold, classify as DR
                         Lower values = more sensitive to mild DR (Grade 1)

    Returns:
        dict with classification results
    """
    # Convert inputs to model dtype (FP16 if enabled)
    if model_manager.use_fp16:
        vessel_input = vessel_input.half()
        green_input = green_input.half()

    # Ensure Stage 1 model is in eval mode
    model_manager.stage1_cascade.eval()

    results = {
        "has_dr": False,
        "severity": "No DR",
        "grade": 0,
        "confidence": 0.0,
        "stage1_result": None,
        "stage2_result": None,
        "stage3_result": None
    }

    # Stage 1: DR vs No-DR (Threshold-based for better Grade 1 detection)
    with torch.no_grad():
        # Get predictions from Cascade model (VDMDR-trained)
        cascade_logits, _, _, _ = model_manager.stage1_cascade(
            vessel_input, green_input
        )
        cascade_probs = F.softmax(cascade_logits, dim=1)

        prob_no_dr = cascade_probs[0, 0].item()
        prob_dr = cascade_probs[0, 1].item()

        # Use threshold instead of argmax for better sensitivity
        # If P(DR) >= threshold, classify as DR (proceed to Stage 2)
        has_dr = prob_dr >= stage1_threshold

    if not has_dr:  # No DR
        results["has_dr"] = False
        results["severity"] = "No DR"
        results["grade"] = 0
        results["confidence"] = prob_no_dr
        results["stage1_result"] = f"No DR (P(DR)={prob_dr:.3f})"
        return results

    # Has DR - proceed to Stage 2
    results["has_dr"] = True
    results["stage1_result"] = "DR (Ensemble)"

    # Stage 2: Early (1-2) vs Advanced (3-4) DR
    # Lazy load Stage 2 model (only when DR is detected)
    model_manager.load_stage2()

    with torch.no_grad():
        main_logits, _, _, _ = model_manager.stage2_model(vessel_input, green_input)
        probs = F.softmax(main_logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
        stage2_confidence = probs[0, pred].item()

    if pred == 0:  # Early DR (Grade 1-2)
        results["stage2_result"] = "Early DR"

        # Stage 3a: Grade 1 vs 2
        # Lazy load Stage 3a model (only for Early DR cases)
        model_manager.load_stage3a()

        with torch.no_grad():
            main_logits, _, _, _ = model_manager.stage3a_model(vessel_input, green_input)
            probs = F.softmax(main_logits, dim=1)
            pred = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred].item()

        if pred == 0:
            results["severity"] = "Grade 1"
            results["grade"] = 1
            results["stage3_result"] = "Grade 1"
        else:
            results["severity"] = "Grade 2"
            results["grade"] = 2
            results["stage3_result"] = "Grade 2"
        results["confidence"] = confidence

    else:  # Advanced DR (Grade 3-4)
        results["stage2_result"] = "Advanced DR"

        # Stage 3b: Grade 3 vs 4
        # Lazy load Stage 3b model (only for Advanced DR cases)
        model_manager.load_stage3b()

        with torch.no_grad():
            main_logits, _, _, _ = model_manager.stage3b_model(vessel_input, green_input)
            probs = F.softmax(main_logits, dim=1)
            pred = torch.argmax(probs, dim=1).item()
            confidence = probs[0, pred].item()

        if pred == 0:
            results["severity"] = "Grade 3"
            results["grade"] = 3
            results["stage3_result"] = "Grade 3"
        else:
            results["severity"] = "Grade 4"
            results["grade"] = 4
            results["stage3_result"] = "Grade 4"
        results["confidence"] = confidence

    return results
