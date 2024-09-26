from flask import Flask, render_template, request, redirect, session
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Установите свой секретный ключ

# Создание директории для выходных файлов
output_directory = 'size_output'
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        product_data = request.form.get('product_data', '')
        csv_file = request.files.get('csv_file')

        output_messages = []  # Список для хранения сообщений

        # Обработка данных из текстового поля
        file_row_counts = {}
        if product_data:
            product_lines = product_data.splitlines()
            for line in product_lines:
                parts = line.split('\t')
                if len(parts) == 2:
                    product_name = parts[0].strip()
                    product_count = int(parts[1].strip())
                    file_row_counts[product_name] = product_count

        # Проверка на загруженный файл CSV
        if csv_file and csv_file.filename.endswith('.csv'):
            upload_dir = 'size'
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            uploaded_file_path = os.path.join(upload_dir, csv_file.filename)
            csv_file.save(uploaded_file_path)
            output_messages.append(f"Файл CSV успешно загружен: {csv_file.filename}")

            # Обработка файлов
            source_files = [uploaded_file_path]

            for source_file in source_files:
                source_file_name = os.path.basename(source_file).split('.')[0]
                output_sub_directory = os.path.join(output_directory, source_file_name)
                if not os.path.exists(output_sub_directory):
                    os.makedirs(output_sub_directory)

                with open(source_file, 'r') as file_handle:
                    for product_name, row_count in file_row_counts.items():
                        output_file_path = os.path.join(output_sub_directory, f"{product_name}.csv")
                        with open(output_file_path, 'w') as output_handle:
                            lines_written = 0
                            for _ in range(row_count):
                                line = file_handle.readline()
                                if not line:  # Если достигнут конец файла
                                    break
                                output_handle.write(line)
                                lines_written += 1

                            output_messages.append(f"Файл {output_file_path} успешно создан.")

        session['output_messages'] = output_messages
        return redirect('/')

    output_messages = session.get('output_messages', [])
    session.pop('output_messages', None)  # Очищаем сообщения после отображения
    return render_template('index.html', output_messages=output_messages)

if __name__ == '__main__':
    app.run(debug=True)
