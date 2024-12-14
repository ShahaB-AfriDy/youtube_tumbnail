import requests
import streamlit as st
import json
import time
from io import BytesIO
from PIL import Image


BRAND_ID = "6710be8d32ae85ca03b7a703"
API_KEY = "F3GQX4vAYvPOQMwslg8YPn3KNKcj6DWK"


def create_content(prompt_text, website_name, brand_handle, logo_url):
    url = "https://brain.predis.ai/predis_api/v1/create_content/"

    brand_details = {
        "brand_website": website_name,
        "brand_handle": "@"+brand_handle,
        "logo_url": logo_url
    }

    payload = {
        "brand_id": BRAND_ID,
        "text": prompt_text,
        "media_type": "single_image",
        "color_palette_type": "brand",
        "brand_details": json.dumps(brand_details)
    }

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        json_response = response.json()
        return json_response.get('post_ids', [None])[0]
    else:
        st.error("Error occurred during content creation - {}".format(response.text))
        return None


def check_post_status(post_id, Flag=True):
    url = "https://brain.predis.ai/predis_api/v1/get_posts/"
    payload = {
        "brand_id": BRAND_ID,
        "media_type": "single_image",
        "page_n": 1,
        "items_n": 1
    }

    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }

    if Flag:
        progress_bar = st.progress(0)
        for i in range(1, 41):
            progress_bar.progress(i / 40)
            time.sleep(1)

    response = requests.get(url, params=payload, headers=headers)

    if response.status_code == 200:
        posts = response.json().get('posts', [])
        if posts:
            recent_post = posts[0]  # Get the most recent post
            post_status = recent_post['status']
            if post_status == 'completed':
                return recent_post['generated_media'][0]['url']
            elif post_status == 'error':
                st.error("An error occurred during image generation.")
                return None
            else:
                st.write("Image generation still in progress...")
        else:
            st.error("No posts found in response.")
            return None
    else:
        st.error(f"Error occurred while checking post status - {response.text}")
        return None


def download_image(image_url, size):
    img_response = requests.get(image_url)
    img = Image.open(BytesIO(img_response.content))

    if size == "youtube_thumbnail":
        img = img.resize((1280, 720))
    elif size == "medium":
        img = img.resize((800, 600))
    elif size == "full":
        pass

    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


st.markdown("""
    <style>
        .css-1emrehy.edgvbvh3 {
            height: 100px;
        }
        .css-1emrehy.edgvbvh3 textarea {
            height: 100px;
        }
        .css-ffhzg2 {
            color: #4CAF50;
            font-family: 'Arial', sans-serif;
            font-size: 36px;
        }
        .css-1d391kg {
            background-color: #2E3B4E;
            color: #ffffff;
        }
        .stButton button {
            background-color: #FF5733;
            color: black;
            border-radius: 8px;
            font-size: 18px;
        }
        .stButton button:hover {
            background-color: #FF5733;
            color: white;
        }
        .stDownloadButton button {
            background-color: #28A745;
            color: white;
            border-radius: 8px;
            font-size: 14px;
        }
        .stDownloadButton button:hover {
            background-color: #28A745;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#4CAF50; font-family: Arial, sans-serif; font-size: 36px;'>Post AI Design Generation</h1>", unsafe_allow_html=True)

prompt_text = st.text_area(label="", placeholder="What is your post about", height=100)

st.markdown("<br>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Enter Details")
    website_name = st.text_input("Enter your brand's website (.com):")
    brand_handle = st.text_input("Enter your brand @handle:")
    logo_url = st.text_input("Enter your logo URL:")


col1, col2 = st.columns([1, 1])

with col1:
    generate_button = st.button("Generate Image")

with col2:
    see_last_button = st.button("See Last Post")

if generate_button:
    if prompt_text and website_name and brand_handle and logo_url:
        with st.spinner("Generating image..."):
            post_id = create_content(prompt_text, website_name, brand_handle, logo_url)
            if post_id:
                image_url = check_post_status(post_id)
                if image_url:
                    st.image(image_url, caption="Generated Image", use_container_width=False, width=560)

                    st.download_button(
                        label="Download Square (1080x1080)",
                        data=download_image(image_url, "full"),
                        file_name="generated_image_square.png",
                        mime="image/png",
                        use_container_width=True,
                        key="square_download"
                    )
                    st.download_button(
                        label="Download Portrait (1080x1920)",
                        data=download_image(image_url, "medium"),
                        file_name="generated_image_portrait.png",
                        mime="image/png",
                        use_container_width=True,
                        key="portrait_download"
                    )
                    st.download_button(
                        label="Download Landscape (1280x720)",
                        data=download_image(image_url, "youtube_thumbnail"),
                        file_name="generated_image_landscape.png",
                        mime="image/png",
                        use_container_width=True,
                        key="landscape_download"
                    )

    else:
        st.warning("Please fill out all fields.")


if see_last_button:
    image_url = check_post_status(None, Flag=False)  
    if image_url:
        st.image(image_url, caption="Last Created Post", use_container_width=False, width=560)

        
        st.download_button(
            label="Download Square (1080x1080)",
            data=download_image(image_url, "full"),
            file_name="last_post_square.png",
            mime="image/png",
            use_container_width=True,
            key="last_square_download"
        )
        st.download_button(
            label="Download Portrait (1080x1920)",
            data=download_image(image_url, "medium"),
            file_name="last_post_portrait.png",
            mime="image/png",
            use_container_width=True,
            key="last_portrait_download"
        )
        st.download_button(
            label="Download Landscape (1280x720)",
            data=download_image(image_url, "youtube_thumbnail"),
            file_name="last_post_landscape.png",
            mime="image/png",
            use_container_width=True,
            key="last_landscape_download"
        )
    else:
        st.warning("No previous post found.")
