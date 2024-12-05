import json
from rouge_score import rouge_scorer

ground_truth_path = './val_filtered_annotations.json'
generated_captions_path = './generated_captions.json'


def load_ground_truth(filepath):
    """
    Load ground truth captions from a COCO-style annotations JSON file.
    :param filepath: Path to the ground truth JSON file.
    :return: A dictionary where keys are image_ids and values are lists of captions.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    ground_truth = {}
    for annotation in data["annotations"]:
        image_id = annotation["image_id"]
        caption = annotation["caption"]
        if image_id not in ground_truth:
            ground_truth[image_id] = []
        ground_truth[image_id].append(caption)
    return ground_truth


def load_generated_captions(filepath):
    """
    Load generated captions from a JSON file.
    :param filepath: Path to the generated captions JSON file.
    :return: A dictionary where keys are image_ids and values are single captions.
    """
    with open(filepath, 'r') as f:
        data = json.load(f)
    generated_captions = {entry["image_id"]: entry["caption"] for entry in data}
    return generated_captions


def compute_rouge_l(reference_captions, generated_caption):
    """
    Compute ROUGE-L score for a single image.
    :param reference_captions: List of reference captions for the image.
    :param generated_caption: The caption generated by the model.
    :return: ROUGE-L F1 score as a float.
    """
    scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
    scores = [scorer.score(ref, generated_caption)['rougeL'].fmeasure for ref in reference_captions]
    return max(scores)


if __name__ == "__main__":

    ground_truth = load_ground_truth(ground_truth_path)
    generated_captions = load_generated_captions(generated_captions_path)


    all_rouge_scores = {}
    for image_id, generated_caption in generated_captions.items():
        reference_captions = ground_truth.get(image_id, [])
        if reference_captions:
            try:
                rouge_l = compute_rouge_l(reference_captions, generated_caption)
                all_rouge_scores[image_id] = rouge_l
                print(f"Image ID: {image_id}, ROUGE-L Score: {rouge_l}")
            except Exception as e:
                print(f"Error computing ROUGE-L for image_id {image_id}: {e}")
        else:
            print(f"Warning: No ground truth captions for image_id {image_id}")

    if all_rouge_scores:
        average_rouge_score = sum(all_rouge_scores.values()) / len(all_rouge_scores)
        print("\nAverage ROUGE-L Score:", average_rouge_score)
    else:
        print("No ROUGE-L scores computed; check your input data.")
