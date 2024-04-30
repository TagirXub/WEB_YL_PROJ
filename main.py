import pandas as pd
from flask import Flask, flash, request, redirect, url_for, render_template
from flask_bootstrap import Bootstrap
from werkzeug.utils import secure_filename
from numpy import dot
from numpy.linalg import norm
from PIL import Image
from data import db_session
from data.photos import Photo
import uuid
from flask_wtf import FlaskForm

import timm  # библиотека с нужными моделями
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
model = timm.create_model('swinv2_base_window16_256', pretrained=True, num_classes=1)
config = resolve_data_config({}, model=model)
processorr = create_transform(**config)
model.head.fc = model.head.flatten
db_session.global_init("db/photos.db")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# Проверка файла на нужный формат
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# косинусное расстояние
def cos_sim(v1, v2):
    return dot(v1, v2) / (norm(v1) * norm(v2))


# функция для показа топ 10 картинок
@app.route('/res/<name>', methods=['GET', 'POST'])
def download_file(name):
    """
    короче сначала тут ищется сам эмбединг вместе с путем
    потом идет запись косинусных расстояний со всеми попарно
    дальше сортируем список по косиноснуму расстоянию
    берем топ 10 в список и делаем список путей
    картинки лежат в пути static/dataset
    дальше там рендерится темплейт но тут луччше мне скажите
    проще будет если я быренько там накидаю
    """
    path = f'./static/dataset/{name}'
    ses = db_session.create_session()
    img1 = Image.open(path).convert('RGB')
    img1 = processorr(img1).unsqueeze(0).to('cpu')
    v1 = list(model(img1.to('cpu'))[0].cpu().detach().numpy())
    res = []
    for i in ses.query(Photo).all():
        v2 = i.embedding
        pom = cos_sim(v1, v2)
        if pom >= 0.98:
            continue
        else:
            res.append((i.path, pom))
    res.sort(key=lambda x: -x[-1])
    paths = [i[0] for i in res[:10]]
    print(paths)
    return render_template('img.html', paths=paths)


# Это промежуточное окно между загрузкой файла и показом топ 10
@app.route('/check/<name>', methods=['GET', 'POST'])
def check_file(name):
    """
    просто показываем фотку
    можно добавить чтобы внизу писался класс
    тип вот фотка ее класс ГРафика
    и опиисание еще если успеете
    """
    path = f'/dataset/{name}'
    if request.method == 'POST':
        return redirect(url_for('download_file', name=path.split("/")[-1]))
    else:
        return f'''
    <!doctype html>
    <title>Класс</title>
    <link rel="stylesheet" 
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                    crossorigin="anonymous">
    <h1 style="text-align: center;">Вот ваш файл</h1>
    <div>
    <div class="item active">
                <img src="{url_for('static', filename=path)}"
                     style="max-width:800;max-height:800px;display:block;margin-left:auto;margin-right:auto;">
    <div style="display: flex;
  justify-content: space-around;">
        <button onclick="document.location='/'" class="btn btn-primary">На главную</button>
    <form method=post enctype=multipart/form-data>
      <input class="btn btn-primary" type=submit value=Чекнуть style="display: block;
  margin-left: auto; 
  margin-right: auto;
  margin-top: 10px;
  width: 100px;">
  </div>
    </form>
    </div>
    </html>
    '''


# просто загрузка файла
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Не могу прочитать файл')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('Нет выбранного файла')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            uid = uuid.uuid4()
            file.save(f"static/dataset/{uid}.jpg")
            return redirect(url_for('check_file', name=f'{uid}.jpg'))
    return '''
    <!doctype html>
    <link rel="stylesheet" 
                    href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" 
                    integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" 
                    crossorigin="anonymous">
    <title>Загрузить новый файл</title>
    <div style="text-align:center; margin-top:100px">
    <h1>Загрузить новый файл</h1>
    <form method=post enctype=multipart/form-data>
      <input class="form-control-file" type=file name=file>
      <input class="btn btn-primary" type=submit value=Upload>
    </form>
    </div>
    </html>
    '''


app.secret_key = "super secret key"
app.debug = True
app.run(host='127.0.0.1', threaded=True)
