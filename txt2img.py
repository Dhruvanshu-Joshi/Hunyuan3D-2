import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from PIL import Image
from io import BytesIO
from rembg import remove

def get_relevant_wikipedia_image(article_title: str, show_each=True, save_path=None):
    """
    Fetches relevant images from a Wikipedia article, removes their backgrounds,
    and lets the user choose the best one.

    Args:
        article_title (str): The title of the Wikipedia article.
        show_each (bool): Whether to display each image as it's loaded.
        save_path (str or None): Optional path to save the selected image.

    Returns:
        PIL.Image: The selected image with background removed.
    """

    def get_main_article_image(title):
        title_encoded = title.replace(" ", "_")
        rest_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title_encoded}"
        try:
            res = requests.get(rest_url)
            if res.status_code == 200:
                data = res.json()
                return data.get("originalimage", {}).get("source")
        except Exception as e:
            print(f"Failed to fetch summary JSON: {e}")
        return None

    def is_relevant_image(tag, article_name_lower, lead_image_limit=3):
        parent = tag
        while parent:
            parent_classes = parent.get("class", [])
            if any("infobox" in cls for cls in parent_classes):
                return True
            parent = parent.find_parent()

        fig = tag.find_parent("figure")
        if fig:
            caption = fig.find("figcaption")
            if caption and article_name_lower in caption.get_text().lower():
                return True

        alt_text = tag.get("alt", "").lower()
        if article_name_lower in alt_text:
            return True

        if tag in lead_image_candidates[:lead_image_limit]:
            return True

        return False

    article_name = article_title.replace(" ", "_")
    article_name_lower = article_name.lower()
    fetched_images = []

    # Step 1: Fetch main article image from REST API
    main_image_url = get_main_article_image(article_title)
    if main_image_url:
        try:
            img_data = requests.get(main_image_url).content
            output = remove(img_data)
            pil_img = Image.open(BytesIO(output)).convert("RGBA")
            print(f"\nMain article image: {main_image_url}")
            if show_each:
                pil_img.show(title="Main Article Image")
            fetched_images.append((0, main_image_url, pil_img))
        except Exception as e:
            print(f"Failed to process main article image: {e}")

    # Step 2: Parse HTML for additional images
    url = f"https://en.wikipedia.org/wiki/{article_name}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch page: {url}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", id="mw-content-text")
    img_tags = content_div.find_all("img") if content_div else []
    lead_image_candidates = img_tags[:5]

    for i, img in enumerate(img_tags):
        img_url = img.get("src")
        if not img_url:
            continue

        if img_url.startswith("//"):
            full_url = "https:" + img_url
        elif img_url.startswith("/"):
            full_url = urljoin("https://en.wikipedia.org", img_url)
        elif img_url.startswith("http"):
            full_url = img_url
        else:
            continue

        image_filename = os.path.basename(urlparse(full_url).path).lower()
        if any(x in image_filename for x in ["icon", "logo", "wikimedia", "button", "poweredby"]):
            continue
        if os.path.splitext(image_filename)[1] in [".svg", ".ico", ".png"]:
            continue

        if not is_relevant_image(img, article_name_lower):
            continue

        try:
            img_data = requests.get(full_url).content
            output = remove(img_data)
            pil_img = Image.open(BytesIO(output)).convert("RGBA")
            img_number = len(fetched_images)

            print(f"\nImage #{img_number}: {full_url}")
            if show_each:
                pil_img.show(title=f"Image #{img_number}")
            fetched_images.append((img_number, full_url, pil_img))
        except Exception as e:
            print(f"Failed to process {full_url}: {e}")

    # Step 3: Prompt user to select one
    if not fetched_images:
        print("No relevant images found.")
        return None
    else:
        while True:
            try:
                selected = int(input(f"\nEnter the image number to select (0 to {len(fetched_images)-1}): "))
                if 0 <= selected < len(fetched_images):
                    chosen_image = fetched_images[selected][2]
                    print(f"\nYou selected image #{selected}: {fetched_images[selected][1]}")
                    chosen_image.show(title="Selected Image")

                    if save_path:
                        chosen_image.save(save_path)
                        print(f"Image saved to: {save_path}")

                    return chosen_image
                else:
                    print("Invalid index. Try again.")
            except ValueError:
                print("Please enter a valid number.")

# --- Example usage ---
if __name__ == "__main__":
    img = get_relevant_wikipedia_image("Grey reef shark", save_path="shark_image.png")
