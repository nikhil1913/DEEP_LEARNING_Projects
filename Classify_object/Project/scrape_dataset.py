"""
Dataset Scraper - Recyclable vs Non-Recyclable
===============================================
Yeh script Google aur Bing se images download karegi
20 categories x 250 images = 5000 images total

Install karne ke liye:
    pip install icrawler

Chalane ke liye:
    python scrape_dataset.py
"""

from icrawler.builtin import GoogleImageCrawler, BingImageCrawler
import os
import time

# ─── Categories ───────────────────────────────────────────────────────────────

CATEGORIES = {
    "recyclable": {
        "plastic_bottle":   ["plastic bottle waste recyclable", "empty plastic water bottle", "plastic bottle garbage"],
        "cardboard_box":    ["cardboard box waste", "empty cardboard packaging", "cardboard recycling"],
        "glass_bottle":     ["glass bottle waste recyclable", "empty glass bottle", "glass jar recyclable"],
        "metal_can":        ["metal tin can waste", "aluminium can recyclable", "steel can garbage"],
        "newspaper_paper":  ["newspaper waste pile", "old newspaper recycling", "waste paper recyclable"],
        "notebook_waste":   ["waste notebook paper", "old books paper waste", "torn notebook pages"],
        "aluminium_foil":   ["aluminium foil waste", "crumpled aluminium foil garbage", "foil wrap waste"],
        "steel_utensil":    ["scrap steel utensil", "old steel vessels scrap", "broken steel utensil waste"],
        "tetra_pak":        ["tetra pak juice box waste", "empty juice carton recyclable", "milk carton waste"],
        "fabric_clothes":   ["old clothes waste fabric", "torn clothes garbage", "fabric waste recycling"],
    },
    "non_recyclable": {
        "thermocol":        ["thermocol waste styrofoam", "styrofoam garbage non recyclable", "thermocol packaging waste"],
        "chips_packet":     ["chips packet waste multilayer", "empty chips bag garbage", "snack wrapper waste"],
        "diaper":           ["used diaper waste", "disposable diaper garbage", "baby diaper waste"],
        "cigarette_butt":   ["cigarette butt waste", "cigarette stub garbage", "used cigarette waste"],
        "polythene_bag":    ["polythene bag waste", "plastic carry bag garbage", "thin plastic bag waste"],
        "gutka_packet":     ["gutka pan masala packet waste", "tobacco pouch wrapper garbage", "pan masala wrapper"],
        "broken_glass":     ["broken glass waste mixed", "shattered glass garbage", "broken glass pieces waste"],
        "sanitary_napkin":  ["sanitary napkin waste disposal", "sanitary pad garbage", "menstrual waste disposal"],
        "ceramic_broken":   ["broken ceramic waste", "broken clay pot garbage", "crockery broken waste"],
        "soiled_tissue":    ["used tissue paper waste", "soiled paper garbage", "dirty tissue waste"],
    }
}

IMAGES_PER_CATEGORY = 250  # 250 per category, augmentation baad mein karenge
OUTPUT_DIR = "dataset"     # Root folder


def create_folder(path):
    os.makedirs(path, exist_ok=True)

def count_images(folder):
    if not os.path.exists(folder):
        return 0
    return len([f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))])

def scrape_category(category_type, category_name, queries, target_count):
    """
    Ek category ke liye images scrape karta hai.
    Pehle Google se try karta hai, agar kam images milein to Bing se bhi leta hai.
    """
    save_dir = os.path.join(OUTPUT_DIR, category_type, category_name)
    create_folder(save_dir)

    already_downloaded = count_images(save_dir)
    if already_downloaded >= target_count:
        print(f"  ✅ [{category_name}] Already {already_downloaded} images hain, skip kar rahe hain.")
        return

    remaining = target_count - already_downloaded
    print(f"\n  📥 [{category_name}] {already_downloaded} images hain, {remaining} aur chahiye...")

    per_query = max(1, remaining // len(queries)) + 20  

    # --- Google se scrape ---
    for i, query in enumerate(queries):
        current_count = count_images(save_dir)
        if current_count >= target_count:
            break

        needed = target_count - current_count
        fetch_count = min(needed + 10, per_query)

        print(f"    🔍 Google: '{query}' ({fetch_count} images)...")
        try:
            crawler = GoogleImageCrawler(
                storage={"root_dir": save_dir},
                feeder_threads=2,
                parser_threads=2,
                downloader_threads=4,
            )
            crawler.crawl(
                keyword=query,
                max_num=fetch_count,
                min_size=(100, 100),      
                file_idx_offset='auto',   
            )
        except Exception as e:
            print(f"    ⚠️  Google error: {e}")

        time.sleep(1)  # Rate limiting se bachne ke liye

    #  Agar Google se kam mila to Bing se bhi lo 
    current_count = count_images(save_dir)
    if current_count < target_count:
        remaining_after_google = target_count - current_count
        print(f"    🔄 Google se kam mila ({current_count}), Bing se {remaining_after_google} aur le rahe hain...")

        for query in queries:
            current_count = count_images(save_dir)
            if current_count >= target_count:
                break

            needed = target_count - current_count
            print(f"    🔍 Bing: '{query}' ({needed} images)...")
            try:
                crawler = BingImageCrawler(
                    storage={"root_dir": save_dir},
                    feeder_threads=2,
                    parser_threads=2,
                    downloader_threads=4,
                )
                crawler.crawl(
                    keyword=query,
                    max_num=needed + 10,
                    min_size=(100, 100),
                    file_idx_offset='auto',
                )
            except Exception as e:
                print(f"    ⚠️  Bing error: {e}")

            time.sleep(1)

    final_count = count_images(save_dir)
    print(f"  ✅ [{category_name}] Complete! Total images: {final_count}")



def main():
    print("=" * 60)
    print("  🗑️  Waste Image Dataset Scraper")
    print("  Recyclable vs Non-Recyclable")
    print("=" * 60)
    print(f"\n📁 Dataset save hogi: ./{OUTPUT_DIR}/")
    print(f"🎯 Target: {IMAGES_PER_CATEGORY} images per category")
    print(f"📊 Total categories: 20 (10 recyclable + 10 non-recyclable)")
    print(f"📸 Total target images: {20 * IMAGES_PER_CATEGORY}\n")

    total_downloaded = 0

    for category_type, categories in CATEGORIES.items():
        print(f"\n{'='*60}")
        print(f"  📂 {category_type.upper()} categories")
        print(f"{'='*60}")

        for category_name, queries in categories.items():
            scrape_category(category_type, category_name, queries, IMAGES_PER_CATEGORY)
            total_downloaded += count_images(
                os.path.join(OUTPUT_DIR, category_type, category_name)
            )

    print(f"\n{'='*60}")
    print("  🎉 Scraping Complete!")
    print(f"{'='*60}")
    print(f"\n📊 Final Dataset Summary:\n")

    grand_total = 0
    for category_type, categories in CATEGORIES.items():
        print(f"  [{category_type.upper()}]")
        for category_name in categories:
            folder = os.path.join(OUTPUT_DIR, category_type, category_name)
            count = count_images(folder)
            grand_total += count
            status = "✅" if count >= IMAGES_PER_CATEGORY else "⚠️ "
            print(f"    {status} {category_name:<25} {count} images")
        print()

    print(f"  📸 Grand Total: {grand_total} images")
    print(f"\n✅ Dataset ready hai! Ab augmentation karo.\n")


if __name__ == "__main__":
    main()