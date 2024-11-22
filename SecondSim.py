import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from time import time

# Используем кэширование Streamlit для загрузки данных


@st.cache
def load_data(file_path):
    return pd.read_excel(file_path)

# Функция для обработки данных


def process_data(base_df, target_df):
    results_found = []
    results_exceptions = []
    results_not_found = []

    for index, row in target_df.iterrows():
        primary_number = row['Primary Number']
        backup_number = None

        # Ищем основной номер в базе
        base_row = base_df[base_df['Primary Number'] == primary_number]

        if not base_row.empty:
            # Если резервный номер найден в базе
            backup_number = base_row.iloc[0]['Backup Number']
            if primary_number == backup_number:
                results_exceptions.append((primary_number, backup_number))
            else:
                results_found.append((primary_number, backup_number))
        else:
            # Если номер не найден в базе
            results_not_found.append(primary_number)

    return results_found, results_exceptions, results_not_found

# Функция для параллельной обработки


def parallel_process(base_file, target_file):
    # Загружаем данные с кэшированием
    base_df = load_data(base_file)
    target_df = load_data(target_file)

    # Начинаем обработку
    start_time = time()
    results_found, results_exceptions, results_not_found = process_data(
        base_df, target_df)
    end_time = time()

    processing_time = end_time - start_time
    return results_found, results_exceptions, results_not_found, processing_time


# Интерфейс Streamlit
st.title('Обработка номеров устройств')

# Загрузка файлов
base_file = st.file_uploader("Загрузите файл с базой данных", type=["xlsx"])
target_file = st.file_uploader(
    "Загрузите файл с основными номерами", type=["xlsx"])

if base_file is not None and target_file is not None:
    # Кнопка для запуска обработки
    if st.button('Запустить обработку'):
        st.text("Обработка данных... Пожалуйста, подождите.")

        # Запускаем обработку в многозадачном режиме
        with st.spinner('Идет обработка...'):
            results_found, results_exceptions, results_not_found, processing_time = parallel_process(
                base_file, target_file)

        # Выводим результаты
        st.success(f"Обработка завершена за {processing_time:.2f} секунд.")
        st.write(f"Найдено совпадений: {len(results_found)}")
        st.write(f"Исключений: {len(results_exceptions)}")
        st.write(f"Не найдено: {len(results_not_found)}")

        # Создание итогового DataFrame для сохранения
        result_df = pd.DataFrame({
            'Основной номер': [x[0] for x in results_found],
            'Резервный номер': [x[1] for x in results_found],
            'Основной номер (исключение)': [x[0] for x in results_exceptions],
            'Резервный номер (исключение)': [x[1] for x in results_exceptions],
            'Не найдено': results_not_found
        })

        # Скачивание файла с результатами
        st.download_button(
            label="Скачать итоговый файл",
            data=result_df.to_csv(index=False),
            file_name="results.csv",
            mime="text/csv"
        )

# Внизу страницы добавляем копирайт
st.markdown("""
    <div style="position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);">
        <p style="text-align: center;">© zHeyBunny</p>
    </div>
""", unsafe_allow_html=True)
