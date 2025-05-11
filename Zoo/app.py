from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="qaz1wsx2",
    database="zoo_db"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/animals', methods=['GET', 'POST'])
def search_animals():
    cursor = db.cursor(dictionary=True)
    query = """
            SELECT a.animal_id, a.name, a.type, d.name AS diet, d.type AS diet_type
            FROM Animals a
                     JOIN Diets d ON a.diet_id = d.diet_id \
            """
    filters = []
    if request.method == 'POST':
        name = request.form.get('name')
        animal_type = request.form.get('type')
        if name:
            filters.append(f"a.name LIKE '%{name}%'")
        if animal_type:
            filters.append(f"a.type = '{animal_type}'")
        if filters:
            query += " WHERE " + " AND ".join(filters)

    cursor.execute(query)
    animals = cursor.fetchall()
    return render_template('animals.html', animals=animals)


@app.route('/all_animals', methods=['GET'])
def all_animals():
    cursor = db.cursor(dictionary=True)
    query = """
            SELECT a.animal_id, a.name, a.type, a.birth_date, h.name AS habitat, d.name AS diet, e.full_name AS caretaker 
            FROM Animals a
                     JOIN Diets d ON a.diet_id = d.diet_id 
                     JOIN Habitats h ON a.habitat_id = h.habitat_id
                     LEFT JOIN Employees e ON a.caretaker_id = e.employee_id
            """
    cursor.execute(query)
    animals = cursor.fetchall()
    return render_template('all_animals.html', animals=animals)

@app.route('/add_animal', methods=['GET', 'POST'])
def add_animal():
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        animal_type = request.form.get('type')
        diet_id = request.form.get('diet_id')
        birth_date = request.form.get('birth_date')
        habitat_id = request.form.get('habitat_id')
        caretaker_id = request.form.get('caretaker_id')
        vet_id = request.form.get('vet_id')  # Отримання ID ветеринара

        # Додавання нового запису в базу
        cursor.execute("""
            INSERT INTO Animals (name, type, diet_id, birth_date, habitat_id, caretaker_id, vet_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, animal_type, diet_id, birth_date, habitat_id, caretaker_id, vet_id))
        db.commit()
        return redirect(url_for('all_animals'))

    # Отримання списку доступних ветеринарів
    cursor.execute("SELECT vet_id, full_name FROM Veterinarians")
    veterinarians = cursor.fetchall()

    # Отримання списку доступних дієт
    cursor.execute("SELECT diet_id, name FROM Diets")
    diets = cursor.fetchall()

    # Отримання списку доступних місць існування
    cursor.execute("SELECT habitat_id, name FROM Habitats")
    habitats = cursor.fetchall()

    # Отримання списку працівників
    cursor.execute("SELECT employee_id, full_name FROM Employees")
    employees = cursor.fetchall()

    return render_template('add_animal.html', diets=diets, habitats=habitats, employees=employees, veterinarians=veterinarians)


@app.route('/edit_animal/<int:animal_id>', methods=['GET', 'POST'])
def edit_animal(animal_id):
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        animal_type = request.form.get('type')
        diet_id = request.form.get('diet_id')
        birth_date = request.form.get('birth_date')
        habitat_id = request.form.get('habitat_id')
        caretaker_id = request.form.get('caretaker_id')
        vet_id = request.form.get('vet_id')  # Збереження ID ветеринара

        # Оновлення даних у базі
        cursor.execute("""
            UPDATE Animals
            SET name = %s, type = %s, diet_id = %s, birth_date = %s, habitat_id = %s, caretaker_id = %s, vet_id = %s
            WHERE animal_id = %s
        """, (name, animal_type, diet_id, birth_date, habitat_id, caretaker_id, vet_id, animal_id))
        db.commit()
        return redirect(url_for('search_animals'))

    # Отримання інформації про поточного тварину
    cursor.execute("SELECT * FROM Animals WHERE animal_id = %s", (animal_id,))
    animal = cursor.fetchone()

    # Отримання списку всіх ветеринарів
    cursor.execute("""
                   SELECT v.vet_id, e.full_name
                   FROM Veterinarians v
                            JOIN Employees e ON v.vet_id = e.employee_id;
                   """)
    veterinarians = cursor.fetchall()

    # Отримання списку всіх раціонів
    cursor.execute("SELECT diet_id, name FROM Diets")
    diets = cursor.fetchall()

    # Отримання списку всіх місць існування
    cursor.execute("SELECT habitat_id, name FROM Habitats")
    habitats = cursor.fetchall()

    # Отримання списку працівників
    cursor.execute("SELECT employee_id, full_name FROM Employees")
    employees = cursor.fetchall()

    return render_template('edit_animal.html', animal=animal, diets=diets, habitats=habitats, employees=employees, veterinarians=veterinarians)

@app.route('/families')
def families():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
                   SELECT e1.full_name AS partner1, e1.birth_date AS b1, e1.phone AS p1,
                          e2.full_name AS partner2, e2.birth_date AS b2, e2.phone AS p2
                   FROM FamilyRelations fr
                            JOIN Employees e1 ON fr.employee1_id = e1.employee_id
                            JOIN Employees e2 ON fr.employee2_id = e2.employee_id
                   WHERE fr.relation_type = 'подружжя'
                   """)
    families = cursor.fetchall()
    return render_template('families.html', families=families)

@app.route('/diets')
def diets():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
                   SELECT a.name, d.diet_id, d.name AS diet_name
                   FROM Animals a
                            JOIN Diets d ON a.diet_id = d.diet_id
                   """)
    diets = cursor.fetchall()
    return render_template('diets.html', diets=diets)

@app.route('/edit_family/<int:relation_id>', methods=['GET', 'POST'])
def edit_family(relation_id):
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        employee1_id = request.form.get('employee1_id')
        employee2_id = request.form.get('employee2_id')
        relation_type = request.form.get('relation_type')

        # Оновлення сімейних даних
        cursor.execute("""
            UPDATE FamilyRelations
            SET employee1_id = %s, employee2_id = %s, relation_type = %s
            WHERE relation_id = %s
        """, (employee1_id, employee2_id, relation_type, relation_id))
        db.commit()
        return redirect(url_for('families'))

    # Отримання інформації про обраний зв'язок
    cursor.execute("SELECT * FROM FamilyRelations WHERE relation_id = %s", (relation_id,))
    family = cursor.fetchone()

    # Отримання списку працівників для редагування
    cursor.execute("SELECT employee_id, full_name FROM Employees")
    employees = cursor.fetchall()

    return render_template('edit_family.html', family=family, employees=employees)

@app.route('/add_family', methods=['GET', 'POST'])
def add_family():
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        employee1_id = request.form.get('employee1_id')
        employee2_id = request.form.get('employee2_id')
        relation_type = request.form.get('relation_type')

        # Додавання нової сімейної пари в базу
        cursor.execute("""
            INSERT INTO FamilyRelations (employee1_id, employee2_id, relation_type)
            VALUES (%s, %s, %s)
        """, (employee1_id, employee2_id, relation_type))
        db.commit()
        return redirect(url_for('families'))

    # Отримання списку працівників
    cursor.execute("SELECT employee_id, full_name FROM Employees")
    employees = cursor.fetchall()

    return render_template('add_family.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        full_name = request.form.get('full_name')  # Отримання ПІБ
        marital_status = request.form.get('marital_status')
        phone = request.form.get('phone')  # Отримання номера телефону
        birth_date = request.form.get('birth_date')  # Отримання дати народження

        # Додавання нового запису в таблицю Employees
        cursor.execute("""
            INSERT INTO Employees (full_name, marital_status, phone, birth_date)
            VALUES (%s, %s, %s, %s)
        """, (full_name, marital_status, phone, birth_date))  # Виправлено перемінну "position" на "marital_status"
        db.commit()
        return redirect(url_for('employees'))  # Перехід до сторінки зі списком працівників

    return render_template('add_employee.html')

@app.route('/employees')
def employees():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT employee_id, full_name, marital_status, phone, birth_date FROM Employees")
    employees = cursor.fetchall()
    return render_template('employees.html', employees=employees)

@app.route('/all_habitats', methods=['GET'])
def all_habitats():
    cursor = db.cursor(dictionary=True)
    query = """
            SELECT a.name AS animal_name, h.name AS habitat_name
            FROM Animals a
                     JOIN Habitats h ON a.habitat_id = h.habitat_id
            """
    cursor.execute(query)
    habitats = cursor.fetchall()
    return render_template('all_habitats.html', habitats=habitats)

@app.route('/delete_animal/<int:animal_id>', methods=['POST'])
def delete_animal(animal_id):
    cursor = db.cursor()
    # Видаляємо тварину з таблиці Animals за її ID
    cursor.execute("DELETE FROM Animals WHERE animal_id = %s", (animal_id,))
    db.commit()
    return redirect(url_for('all_animals'))  # Повертаємося до списку всіх тварин

@app.route('/delete_employee/<int:employee_id>', methods=['POST'])
def delete_employee(employee_id):
    cursor = db.cursor()
    # Видаляємо працівника з таблиці Employees за його ID
    cursor.execute("DELETE FROM Employees WHERE employee_id = %s", (employee_id,))
    db.commit()
    return redirect(url_for('employees'))  # Повертаємося до списку всіх працівників

if __name__ == '__main__':
    app.run(debug=True)
