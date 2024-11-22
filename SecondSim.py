import streamlit as st
import pandas as pd
from io import BytesIO
import time  # Импортируем модуль для работы с временем

# Функция для обработки файлов


def process_files(base_file, target_file):
    # Читаем файлы
    base_df = pd.read_excel(base_file)
    target_df = pd.read_excel(target_file)

    # Переименуем столбцы базы для удобства
    base_df.columns = ['Primary', 'Backup']
    target_df.columns = ['Primary']

    # Создаем DataFrame для результатов
    found_df = pd.DataFrame(columns=['Primary', 'Backup'])  # Для совпадений
    exceptions_df = pd.DataFrame(
        columns=['Base Primary', 'Base Backup'])  # Для исключений
    not_found_df = pd.DataFrame(columns=['Not Found'])  # Для не найденных

    # 1. Найдем совпадения по 'Primary' с соответствующим 'Backup' из базы
    found_df = pd.merge(target_df, base_df, on='Primary', how='left')

    # 2. Для исключений, где 'Primary' не найден в 'Primary', но есть в 'Backup'
    exceptions_df = base_df[base_df['Backup'].isin(target_df['Primary'])]

    # 3. Для не найденных, где 'Primary' из target_df не найден в базе
    not_found_df = target_df[~target_df['Primary'].isin(
        base_df['Primary']) & ~target_df['Primary'].isin(base_df['Backup'])]

    # Теперь исключаем из found_df те номера, которые попали в исключения или не были найдены
    found_df = found_df[~found_df['Primary'].isin(exceptions_df['Backup'])]
    found_df = found_df[~found_df['Primary'].isin(not_found_df['Primary'])]

    # Формируем итоговый Excel-файл
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        found_df[['Primary', 'Backup']].to_excel(writer, index=False, startcol=0, startrow=0, header=[
                                                 'Primary', 'Backup'], sheet_name='Sheet1')
        exceptions_df[['Primary', 'Backup']].to_excel(writer, index=False, startcol=3, startrow=0, header=[
                                                      'Base Primary', 'Base Backup'], sheet_name='Sheet1')
        not_found_df[['Primary']].to_excel(writer, index=False, startcol=6, startrow=0, header=[
                                           'Not Found'], sheet_name='Sheet1')

    output.seek(0)
    return output


# Интерфейс Streamlit
st.title("Обработка резервных номеров")
st.write("Загрузите файлы и начните обработку.")

# Загрузка файлов
base_file = st.file_uploader(
    "Загрузите файл с Базой номеров (xlsx)", type="xlsx")
target_file = st.file_uploader(
    "Загрузите файл с основными номерами (xlsx)", type="xlsx")

if st.button("Запустить"):
    if base_file is not None and target_file is not None:
        start_time = time.time()  # Засекаем время начала

        with st.spinner("Обработка..."):
            result = process_files(base_file, target_file)

        end_time = time.time()  # Засекаем время окончания
        processing_time = end_time - start_time  # Вычисляем время выполнения

        st.success(f"Обработка завершена! Время выполнения: {
                   processing_time:.2f} секунд.")
        st.download_button("Скачать результат", data=result,
                           file_name="result.xlsx")
    else:
        st.error("Пожалуйста, загрузите оба файла.")

# Знак копирайта
st.markdown("---")
st.markdown("<p style='text-align: center;'>© zHeyBunny</p>",
            unsafe_allow_html=True)
