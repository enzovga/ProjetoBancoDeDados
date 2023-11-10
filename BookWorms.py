import sqlite3
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import print

# Define global variables
current_user_id = None

console = Console()

class Livro:
    def __init__(self, titulo, autor, descricao, cover_image_url, data_publicacao, editora, isbn):
        self.titulo = titulo
        self.autor = autor
        self.descricao = descricao
        self.cover_image_url = cover_image_url
        self.data_publicacao = data_publicacao
        self.editora = editora
        self.isbn = isbn

class Usuario:
    def __init__(self, id, username, email, senha_hash):
        self.id = id
        self.username = username
        self.email = email
        self.senha_hash = senha_hash

class Avaliacao:
    def __init__(self, id, user_id, livro_id, rating, review_text):
        self.id = id
        self.user_id = user_id
        self.livro_id = livro_id
        self.rating = rating
        self.review_text = review_text

class ListaLeitura:
    def __init__(self, id, user_id, livro_id):
        self.id = id
        self.user_id = user_id
        self.livro_id = livro_id

def setup_database():
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS Livro (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        titulo TEXT,
                        autor TEXT,
                        descricao TEXT,
                        cover_image_url TEXT,
                        data_publicacao TEXT,
                        editora TEXT,
                        isbn TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Usuario (
                        id INTEGER PRIMARY KEY,
                        username TEXT,
                        email TEXT,
                        senha_hash TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Avaliacao (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        livro_id INTEGER,
                        rating INTEGER,
                        review_text TEXT,
                        FOREIGN KEY (user_id) REFERENCES Usuario(id),
                        FOREIGN KEY (livro_id) REFERENCES Livro(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS ListaLeitura (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER,
                        livro_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES Usuario(id),
                        FOREIGN KEY (livro_id) REFERENCES Livro(id))''')

    connection.commit()
    connection.close()

def insert_book(livro):
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('''INSERT INTO Livro (titulo, autor, descricao, cover_image_url, data_publicacao, editora, isbn) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (livro.titulo, livro.autor, livro.descricao, livro.cover_image_url, livro.data_publicacao, livro.editora, livro.isbn))

    connection.commit()
    connection.close()

def get_all_books():
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Livro')
    books = cursor.fetchall()

    connection.close()
    return books

def register_user(id, username, email, senha):
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('''INSERT INTO Usuario (id, username, email, senha_hash)
                      VALUES (?, ?, ?, ?)''', 
                   (id, username, email, senha))

    connection.commit()
    connection.close()

def login(username, senha):
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM Usuario WHERE username = ? AND senha_hash = ?', (username, senha))
    user = cursor.fetchone()

    connection.close()
    
    if user:
        return user[0]
    else:
        return None


def register_genre(id, nome):
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('''INSERT INTO Genero (id, nome)
                      VALUES (?, ?)''', 
                   (id, nome))

    connection.commit()
    connection.close()

def add_book_to_reading_list(livro_id):
    global current_user_id
    if current_user_id is None:
        print("Usuário não logado.")
        return

    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    # Generate a new id for the reading list entry
    cursor.execute('SELECT MAX(id) FROM ListaLeitura')
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1

    cursor.execute('''INSERT INTO ListaLeitura (id, user_id, livro_id)
                      VALUES (?, ?, ?)''', 
                   (new_id, current_user_id, livro_id))

    connection.commit()
    connection.close()

def get_reading_list():
    global current_user_id
    if current_user_id is None:
        print("Usuário não logado.")
        return []

    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('''SELECT Livro.* FROM Livro
                      JOIN ListaLeitura ON Livro.id = ListaLeitura.livro_id
                      WHERE ListaLeitura.user_id = ?''', (current_user_id,))

    books = cursor.fetchall()

    connection.close()
    return books

def add_review(user_id, livro_id, rating, review_text):
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    # Generate a new id for the review
    cursor.execute('SELECT MAX(id) FROM Avaliacao')
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1

    cursor.execute('''INSERT INTO Avaliacao (id, user_id, livro_id, rating, review_text)
                      VALUES (?, ?, ?, ?, ?)''',
                   (new_id, user_id, livro_id, rating, review_text))

    connection.commit()
    connection.close()

def get_reviews_for_book(livro_id):
    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    cursor.execute('''SELECT Usuario.username, Avaliacao.rating, Avaliacao.review_text
                      FROM Avaliacao
                      JOIN Usuario ON Avaliacao.user_id = Usuario.id
                      WHERE Avaliacao.livro_id = ?''', (livro_id,))

    reviews = cursor.fetchall()

    connection.close()
    return reviews

def add_review_ui():
    global current_user_id
    if current_user_id is None:
        print("Usuário não logado.")
        return

    print("\nAdicione uma avaliação.")
    livro_id = Prompt.ask("ID do Livro")
    rating = Prompt.ask("Escolha a avaliação (1-5)", choices=["1", "2", "3", "4", "5"])
    review_text = Prompt.ask("Insira sua review")
    add_review(current_user_id, livro_id, rating, review_text)
    print("Avaliação enviada com")

def view_reviews_ui():
    print("\nVer avaliações de um livro")
    livro_id = input("ID do Livro: ")
    reviews = get_reviews_for_book(livro_id)
    if reviews:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Usuário", style="dim")
        table.add_column("Nota", justify="center")
        table.add_column("Avaliação")

        for username, rating, review_text in reviews:
            stars = "*" * rating + "." * (5 - rating)
            table.add_row(username, stars, review_text)

        console.print(table)
    else:
        print("Não foram encontradas avaliações para este livro.")

def display_main_menu():
    global current_user_id
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Opção", style="dim", width=12)
    table.add_column("Ação")

    if current_user_id is None:
        table.add_row("1", "Login de usuário")
        table.add_row("2", "Registro de usuário")
    else:
        table.add_row("1", "Adicione um livro")
        table.add_row("2", "Lista dos livros")
        table.add_row("3", "Adicionar livro à lista de leitura")
        table.add_row("4", "Ver lista de leitura")
        table.add_row("5", "Adicione uma avaliação")
        table.add_row("6", "Ver avaliações de um livro")
        table.add_row("7", "Sair da conta")

    table.add_row("8", "Sair")
    console.print(table)

def main_menu():
    global current_user_id
    
    while True:
        display_main_menu()
        choice = Prompt.ask("Insira sua escolha")

        if choice == '1':
            if current_user_id is None:
                user_login_ui()
            else:
                add_book_ui()
        elif choice == '2':
            if current_user_id is None:
                register_user_ui()
            else:
                list_books_ui()
        elif choice == '3' and current_user_id is not None:
            add_book_to_reading_list_ui()
        elif choice == '4' and current_user_id is not None:
            view_reading_list_ui()
        elif choice == '5' and current_user_id is not None:
            add_review_ui()
        elif choice == '6' and current_user_id is not None:
            view_reviews_ui()
        elif choice == '7' and current_user_id is not None:
            current_user_id = None
            print("Deslogado com sucesso.")
        elif choice == '8':
            print("Fechando a aplicação.")
            break
        else:
            console.print("[bold red]Opção errada, tente novamente[/bold red]")

def add_book_ui():
    print("\nAdicione um novo livro.")
    titulo = Prompt.ask("Título:")
    autor = Prompt.ask("Autor:")
    descricao = Prompt.ask("Descrição:")
    cover_image_url = Prompt.ask("Imagem URL:")
    data_publicacao = Prompt.ask("Data de Publicação:")
    editora = Prompt.ask("Editora:")
    isbn = Prompt.ask("ISBN:")
    livro = Livro(titulo, autor, descricao, cover_image_url, data_publicacao, editora, isbn)
    insert_book(livro)
    print(f"Livro '{titulo}' adicionado com sucesso!")

def list_books_ui():
    print("\nLista de Todos os Livros")
    books = get_all_books()
    if books:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=12)
        table.add_column("Título")
        table.add_column("Autor")
        table.add_column("Data de Publicação")

        for book in books:
            table.add_row(str(book[0]), book[1], book[2], book[5])

        console.print(table)
    else:
        print("Sem livros disponíveis.")


def user_login_ui():
    global current_user_id

    print("\nLogin de Usuário")
    username = Prompt.ask("Insira o usuário:", default="usuário")
    senha = Prompt.ask("Senha:", password=True)
    user_id = login(username, senha) 
    if user_id:
        current_user_id = user_id  
        print("Login realizado!")
        return True
    else:
        print("Login falhou.")
        return False
    
def register_user_ui():
    print("\nRegistro de Usuário")
    username = Prompt.ask("Insira um usuário", default="usuário")
    email = Prompt.ask("email")
    senha = Prompt.ask("senha", password=True)

    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()
    cursor.execute('SELECT MAX(id) FROM Usuario')
    max_id = cursor.fetchone()[0]
    new_id = 1 if max_id is None else max_id + 1

    register_user(new_id, username, email, senha)
    print("Registro realizado com sucesso, realize o login.")


def add_book_to_reading_list_ui():
    print("\nInsira o ID do livro para adicionar à lista de leitura")
    livro_id = input("ID do Livro: ")
    add_book_to_reading_list(livro_id)
    print("Livro adicionado à lista de leitura.")

def view_reading_list_ui():
    print("\nSua lista de leitura")
    books = get_reading_list()
    if books:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=12)
        table.add_column("Título")
        table.add_column("Autor")

        for book in books:
            table.add_row(str(book[0]), book[1], book[2])

        console.print(table)
    else:
        print("Nenhum livro em sua lista de leitura.")

def initial_books_insert():
    books_to_insert = [
        ("Dom Casmurro", "Machado de Assis", "Descrição de Dom Casmurro", "url_da_imagem1", "1899", "Editora A", "ISBN0001"),
        ("A Moreninha", "Joaquim Manuel de Macedo", "Descrição de A Moreninha", "url_da_imagem2", "1844", "Editora B", "ISBN0002"),
        ("Memórias Póstumas de Brás Cubas", "Machado de Assis", "Descrição de Memórias Póstumas de Brás Cubas", "url_da_imagem3", "1881", "Editora C", "ISBN0003"),
        ("O Guarani", "José de Alencar", "Descrição de O Guarani", "url_da_imagem4", "1857", "Editora D", "ISBN0004"),
        ("Iracema", "José de Alencar", "Descrição de Iracema", "url_da_imagem5", "1865", "Editora E", "ISBN0005"),
        ("Vidas Secas", "Graciliano Ramos", "Descrição de Vidas Secas", "url_da_imagem6", "1938", "Editora F", "ISBN0006"),
        ("O Sítio do Picapau Amarelo", "Monteiro Lobato", "Descrição de O Sítio do Picapau Amarelo", "url_da_imagem7", "1920", "Editora G", "ISBN0007"),
        ("Macunaíma", "Mário de Andrade", "Descrição de Macunaíma", "url_da_imagem8", "1928", "Editora H", "ISBN0008"),
        ("A Moreninha", "Bernardo Guimarães", "Descrição de A Moreninha", "url_da_imagem9", "1844", "Editora I", "ISBN0009"),
    ]

    connection = sqlite3.connect('dbuser.db')
    cursor = connection.cursor()

    for book in books_to_insert:
        cursor.execute('''INSERT INTO Livro (titulo, autor, descricao, cover_image_url, data_publicacao, editora, isbn) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', book)

    connection.commit()
    connection.close()
    print("Initial book data inserted successfully.")


if __name__ == '__main__':
    setup_database()
    initial_books_insert()
    main_menu()

