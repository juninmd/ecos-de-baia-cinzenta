import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

def run_chapter_batch_processing(chapter_list, worker_func, max_workers):
    """
    Runs a batch of chapter processing tasks concurrently using ThreadPoolExecutor.

    Args:
        chapter_list: A list of chapter numbers to process.
        worker_func: A callable that takes a chapter_num and returns True/False for success.
        max_workers: Maximum number of concurrent threads.

    Returns:
        The number of successfully processed chapters.
    """
    success_count = 0
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker_func, chapter_num): chapter_num for chapter_num in chapter_list}
        for future in as_completed(futures):
            try:
                if future.result():
                    success_count += 1
            except Exception as e:
                chapter_num = futures[future]
                print(f"❌ Error processing chapter {chapter_num}: {e}")

    return success_count

def build_common_argparser(description="Process Chapters"):
    """
    Builds an ArgumentParser with the standard CLI arguments shared across generator scripts.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("chapters", type=str, help="Chapter number, list (1,2,3) or range (10-14)")
    parser.add_argument("--style", default="neo-noir cinematic cyberpunk", help="Visual style modifier")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum number of concurrent workers")
    return parser
