import pandas as pd
import streamlit as st
from concurrent.futures import ThreadPoolExecutor
import time

# Функция для обработки данных
def process_data(row, base_df):
    try:
        primary_number = row['Primary Number']
    except KeyError:
        print("Ошибка: Столбец 'Primary Number' не найден")
        return None
    
    # Найдем резервный номер для основного
    backup_number = base_df[base_df['Primary Number'] == primary_number]['Backup Number']
    
    if not backup_number.empty:
        backup_number = backup_number.iloc[0]
        return primary_number, backup_number
    else:
        return primary_number, None

# Функция для параллельной обработки данных
def parallel_process(base_file, target_file):
    base_df = pd.read_excel(base_file, header=None)
    target_df = pd.read_excel(target_file, header=None)
    
    # Присваиваем имена столбцов
    base_df.columns = ['Primary Number', 'Backup Number']
    target_df.columns = ['Primary Number']
    
    # Результаты
    results_found = []
    results_exceptions = []
    results_not_found = []
    
    # Обработка строк с использованием параллельных потоков
    with ThreadPoolExecutor() as executor:
        futures = []
        for idx, row in target_df.iterrows():
            futures.append(executor.submit(process_data, row, base_df))
        
        for future in futures:
            result = future.result()
            if result:
                primary_number, backup_number = result
                if backup_number:
                    results_found.append((primary_number, backup_number))
                else:
                    results_not_found.append(primary_number)
    
    # Возвращаем результаты
    return results_found, results_exceptions, results_not_found

# Стримлит интерфейс
def main():
    st.title("Поиск резервных номеров")
    
    # Загружаем файлы
    base_file = st.file_uploader("Загрузите файл Базы", type="xlsx")
    target_file = st.file_uploader("Загрузите файл с основными номерами", type="xlsx")
    
    if base_file and target_file:
        if st.button('Запустить'):
            with st.spinner('Обработка файлов...'):
                start_time = time.time()
                results_found, results_exceptions, results_not_found = parallel_process(base_file, target_file)
                processing_time = time.time() - start_time
                
                st.success(f"Обработка завершена за {processing_time:.2f} секунд")
                
                # Создание итогового DataFrame
                result_df = pd.DataFrame(columns=["Primary Number", "Backup Number", "Exception Primary", "Exception Backup", "Not Found"])
                
                # Заполнение результатов
                for primary, backup in results_found:
                    result_df = pd.concat([result_df, pd.DataFrame([{"Primary Number": primary, "Backup Number": backup, "Exception Primary": None, "Exception Backup": None, "Not Found": None}])], ignore_index=True)
                
                for primary in results_not_found:
                    result_df = pd.concat([result_df, pd.DataFrame([{"Primary Number": primary, "Backup Number": None, "Exception Primary": None, "Exception Backup": None, "Not Found": primary}])], ignore_index=True)
                
                # Сохранение результата
                result_df.to_excel('output.xlsx', index=False)
                st.download_button('Скачать результат', data=open('output.xlsx', 'rb').read(), file_name='output.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                
                # Показать результаты
                st.write(result_df)
                
                # Копирайт
                st.markdown("<p style='text-align: center;'>© zHeyBunny</p>", unsafe_allow_html=True)

# Запуск Streamlit
if __name__ == '__main__':
    main()
