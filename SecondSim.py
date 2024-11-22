import streamlit as st
import pandas as pd
from io import BytesIO

# Функция для обработки файлов


def process_files(base_file, target_file):
    # Читаем файлы
    base_df = pd.read_excel(base_file)
    target_df = pd.read_excel(target_file)

    # Переименуем столбцы базы для удобства
    base_df.columns = ['Primary', 'Backup']
    target_df.columns = ['Primary']

    # Создаём DataFrame для результатов
    found_df = pd.DataFrame(columns=['Primary', 'Backup'])  # Для совпадений
    exceptions_df = pd.DataFrame(
        columns=['Base Primary', 'Base Backup'])  # Для исключений
    not_found_df = pd.DataFrame(columns=['Not Found'])  # Для не найденных

    # Обрабатываем данные
    for _, row in target_df.iterrows():
        target_number = row['Primary']

        # Проверка совпадений
        if target_number in base_df['Primary'].values:
            backup = base_df.loc[base_df['Primary']
                                 == target_number, 'Backup'].values[0]
            found_df = pd.concat([found_df, pd.DataFrame(
                [[target_number, backup]], columns=['Primary', 'Backup'])])
        elif target_number in base_df['Backup'].values:
            base_row = base_df.loc[base_df['Backup'] == target_number]
            exceptions_df = pd.concat([exceptions_df, pd.DataFrame([[base_row['Primary'].values[0], target_number]],
                                                                   columns=['Base Primary', 'Base Backup'])])
        else:
            not_found_df = pd.concat([not_found_df, pd.DataFrame(
                [[target_number]], columns=['Not Found'])])

    # Формируем итоговый Excel-файл
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        found_df.to_excel(writer, index=False, startcol=0, startrow=0, header=[
                          'Primary', 'Backup'], sheet_name='Sheet1')
        exceptions_df.to_excel(writer, index=False, startcol=3, startrow=0, header=['Base Primary', 'Base Backup'],
                               sheet_name='Sheet1')
        not_found_df.to_excel(writer, index=False, startcol=6, startrow=0, header=[
                              'Not Found'], sheet_name='Sheet1')
    output.seek(0)
    return output


# Интерфейс Streamlit
st.title("Обработка резервных номеров")
st.write("Загрузите файлы и начните обработку.")

# Загрузка файлов
base_file = st.file_uploader("Загрузите файл 'База' (xlsx)", type="xlsx")
target_file = st.file_uploader(
    "Загрузите файл с основными номерами (xlsx)", type="xlsx")

if st.button("Запустить"):
    if base_file is not None and target_file is not None:
        with st.spinner("Обработка..."):
            result = process_files(base_file, target_file)
        st.success("Обработка завершена!")
        st.download_button("Скачать результат", data=result,
                           file_name="result.xlsx")
    else:
        st.error("Пожалуйста, загрузите оба файла.")

# Знак копирайта
st.markdown("---")
st.markdown("© zHeyBunny")
