#モジュールとライブラリ
import streamlit as st
from PIL import Image, ImageDraw
from IPython.display import display
import face_recognition
import time
import matplotlib.pyplot as plt
import numpy as np
import os


st.title('顔画像マスク処理アプリ')
expander1 = st.expander("機能説明")
expander1.write("このアプリは顔画像にマスクを適用し、処理された画像を表示およびダウンロードするアプリケーション。")
expander2 = st.expander("確認された不具合")
expander2.write("顔認識の精度がさほど高くないので、顔が認識されない場合もあります。また、ダウンロードボタンを押すとページ全体がリロードされ、実行し直す必要があるかもしれません。")
#顔認識
def face_square(input_image):
  face_locations = face_recognition.face_locations(input_image)
  base_image = Image.fromarray(input_image)
  draw = ImageDraw.Draw(base_image)

  for (top, right, bottom, left) in face_locations:
      draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255), width=3)

  del draw
  return base_image

#顔画像マスク
def face_mask_full(input_image,mask_image):
  face_locations = face_recognition.face_locations(input_image)
  base_image = Image.fromarray(input_image)
  base_image = base_image.convert('RGBA')
  

  for (top, right, bottom, left) in face_locations:
      tmp_image = mask_image.resize((right-left+50,bottom-top+50))
      img_clear = Image.new('RGBA', base_image.size, (255, 255, 255, 0))
      img_clear.paste(tmp_image, (left-25, top-25))
      base_image = Image.alpha_composite(base_image, img_clear)
  return base_image

#ファイル名チェック
def is_valid_filename(filename):
    if not filename:
        return False
    if not filename.endswith('.png'):
        st.warning("ファイルはPNG形式で保存してください。")
        return False
    return True



#顔画像アップロード
uploaded_target_file = st.file_uploader("**顔画像をここにアップロードしてください...**", type = 'jpg')

if uploaded_target_file is not None:
    
    target_image = face_recognition.load_image_file(uploaded_target_file)
    'アップロード完了'
    if st.checkbox('**画像プレビュー**', key=1):
        preview = face_square(target_image)
        st.image(preview, caption = 'Uploader Image.', use_column_width=True)


#マスク画像アップロード
uploaded_mask_file = st.file_uploader("**マスク画像をここにアップロードしてください...**", type = 'png')

if uploaded_mask_file is not None:
    mask_icon = Image.open(uploaded_mask_file)
    'アップロード完了'
    if st.checkbox('**画像プレビュー**', key=2):
        st.image(mask_icon, caption = 'Uploader Image.', use_column_width=True)

    

#結果出力と保存
if 'iteration' not in st.session_state:
    st.session_state.iteration = 0
if 'filename' not in st.session_state:
    st.session_state.filename = "facemask.png"
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False  # Initialize is_processing as False

if uploaded_target_file and uploaded_mask_file is not None:
    if st.button("**処理開始**", key=3):
        result_image = face_mask_full(target_image, mask_icon)
        st.session_state.iteration = 0
        st.session_state.is_processing = True

    if st.session_state.is_processing:
        latest_iteration = st.empty()
        bar = st.progress(st.session_state.iteration)
        while st.session_state.iteration < 100:
            latest_iteration.text(f'処理中 {st.session_state.iteration + 1}%')
            bar.progress(st.session_state.iteration + 1)
            time.sleep(0.01)
            st.session_state.iteration += 1
        st.session_state.is_processing = False
        latest_iteration.empty()
        bar.empty()
        st.image(result_image, caption='Processed Image.', use_column_width=True)
        st.success('処理完了')
        
        if is_valid_filename(st.session_state.filename):
            result_image.save(st.session_state.filename)
            with open(st.session_state.filename, "rb") as f:
                byte_data = f.read()
            st.download_button(
                label="出力画像ダウンロード",
                data=byte_data,
                file_name=st.session_state.filename,
                mime='image/png',
                key=5)
        else:
            st.warning("ファイルはPNG形式で保存してください。")



        