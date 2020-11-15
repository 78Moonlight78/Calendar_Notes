# -*- coding: utf-8 -*-
import sys
import os
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel
from PyQt5.QtWidgets import QInputDialog, QMessageBox, QComboBox
from PyQt5.QtCore import Qt


NAME_NOTES = 'name_notes.txt'
NAME_DB = 'developments.db'


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.con = sqlite3.connect(NAME_DB)
        self.cursor = self.con.cursor()
        self.show_calendar_window()

    #def keyPressEvent(self, event):
        #if event.key() == "":
            #pass
    #показ окна заметок   
    def show_zam(self):
        uic.loadUi('zametki.ui', self)
        self.btn_calendar2.clicked.connect(self.show_developments_window)
        self.btn_dv2.clicked.connect(self.show_calendar_window)
        self.btn_saving.clicked.connect(self.saving_notes)
        self.btn_create.clicked.connect(self.creating_notes)
        self.btn_del.clicked.connect(self.delet_notes)
        self.listWidget.itemClicked.connect(self.show_note)
        with open(NAME_NOTES, 'r') as file:
            text = file.readlines()
            for i in range(len(text)):
                self.listWidget.insertItem(i, text[i])

    #показ окна календаря для заполнения
    def show_calendar_window(self):
        uic.loadUi('calendar.ui', self)
        self.btn_zam1.clicked.connect(self.show_zam)
        self.btn_dv1.clicked.connect(self.show_developments_window)
        self.btn_add.clicked.connect(self.add_development)
        if self.comboBox_type.count() == QComboBox().count():
            result = self.cursor.execute("SELECT name FROM types").fetchall()
            for type_ in result:
                self.comboBox_type.addItem(type_[0])
    

    #показ окна событий
    def show_developments_window(self):
        uic.loadUi('developments.ui', self)
        self.btn_calendar.clicked.connect(self.show_calendar_window)
        self.btn_zam.clicked.connect(self.show_zam)
        self.btn_dv_del.clicked.connect(self.del_developments)
        self.calendarWidget.clicked.connect(self.show_developmets_list)
        self.btn_show.clicked.connect(self.show_else_dv)

    
    #создание новой заметки 
    def creating_notes(self):
        name, ok_pressed = QInputDialog.getText(self, "Название", "Введите название заметки")
        if ok_pressed:
            with open(name, 'w'):
                pass
            with open(NAME_NOTES, 'a') as file:
                file.write(name + '\n')

            with open(NAME_NOTES, 'r') as file:
                lenght = len(file.readlines())
                
            self.listWidget.insertItem(lenght - 1, name)

    #удаление заметки             
    def delet_notes(self):
        name_notes = self.listWidget.currentItem()
        if name_notes != None:
            valid = QMessageBox.question(self, '', "Действительно удалить заметку",
                QMessageBox.Yes, QMessageBox.No)
            if valid == QMessageBox.Yes:
                name_notes = name_notes.text().replace('\n', '')
                self.listWidget.takeItem(self.listWidget.row(self.listWidget.currentItem()))
                path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name_notes)
                os.remove(path)
                items = [i.text() for i in self.listWidget.selectedItems()]
                self.plainTextEdit.clear()
                with open(NAME_NOTES, 'w') as file:
                    file.write(''.join(items))

        else:
            QMessageBox.question(self, 'Error','Выбирите заметку', QMessageBox.Ok)

    #сохрание заметки     
    def saving_notes(self):
        name_notes = self.listWidget.currentItem()
        if name_notes != None:
            name_notes = name_notes.text().replace('\n', '')
        #получение текста, содержащегося в заметках
            text = self.plainTextEdit.toPlainText()
            with open(name_notes, 'w') as file:
                file.write(text)
        else:
            QMessageBox.question(self, 'Error','Выбирите заметку', QMessageBox.Ok)

    #отображение заметки, считывается информация из файла     
    def show_note(self):
        name_notes = self.listWidget.currentItem()
        if name_notes != None:
            name_notes = name_notes.text().replace('\n', '')
            with open(name_notes, 'r') as file:
                text = file.readlines()
                self.plainTextEdit.clear()
                self.plainTextEdit.appendPlainText(''.join(text))
        else:
            QMessageBox.question(self, 'Error','Выбирите заметку', QMessageBox.Ok)

    #удаление события         
    def del_developments(self):
        data = self.calendarWidget.selectedDate().toString()
        name_and_time = self.listWidget_dv.currentItem()
        if name_and_time != None:
            name, time = name_and_time.text().replace('\n', '').split()
            query_del = '''
            DELETE FROM development
            WHERE name_db = ? and data_db = ? and time_db = ?
            '''
            self.cursor.execute(query_del, (name, data, time))
            self.con.commit()
            self.listWidget_dv.takeItem(self.listWidget_dv.row(self.listWidget_dv.currentItem()))
        else:
            QMessageBox.question(self, 'Error','Выбирите событие', QMessageBox.Ok)

    def show_developmets_list(self):
        self.listWidget_dv.clear()
        choose_data = self.calendarWidget.selectedDate().toString()
        show_dv = '''
        SELECT name_db, time_db from development
            WHERE data_db = ?
        '''
        result = self.cursor.execute(show_dv, (choose_data,)).fetchall()
        self.con.commit()
        for i in range(len(result)):
            self.listWidget_dv.insertItem(i, ' '.join(result[i]))

    def show_else_dv(self):
        data = self.calendarWidget.selectedDate().toString()
        name_and_time = self.listWidget_dv.currentItem()
        if name_and_time != None:
            name, time = name_and_time.text().replace('\n', '').split()
            query_del = '''
            SELECT else_db, type_db FROM development
            WHERE name_db = ? and data_db = ? and time_db = ?
            '''

            query_type = '''
            SELECT name FROM types
            WHERE id = ?
            '''

            else_dv, type_id = self.cursor.execute(query_del, (name, data, time)).fetchall()[0]
            type_name = ' '.join(self.cursor.execute(query_type, (type_id,)).fetchall()[0])
            self.con.commit()
            info = ['Название: '+ name, 'Тип: ' + type_name, 'Дата: ' + data, 'Время: ' + time, 'Другое: ' + else_dv]
            self.creat_dialog_info(info)
             
        else:
            QMessageBox.question(self, 'Error','Выбирите событие', QMessageBox.Ok)

    def creat_dialog_info(self, info):
        dialog = QDialog()
        dialog.setWindowTitle('Событие' + info[0])
        dialog.resize(100, 100) 
        for i in range(5):
            QLabel(info[i], dialog).move(10, 20 * i)   
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()     
    #добавление события
    def add_development(self):
        #имя собыития 
        name = self.line_name.text()
        #время события 
        time = self.timeEdit.time().toString()
        #дата 
        data = self.calendar.selectedDate().toString()
        #дополнение 
        text_else = self.plainTextEdit_else.toPlainText()
        #тип событий 
        type_dv = self.comboBox_type.currentText()

        check_name = '''
        SELECT name_db FROM development
            WHERE time_db = ? and data_db = ? and name_db = ?
        '''
        if len(self.cursor.execute(check_name, (time, data, name)).fetchall()):
            QMessageBox.question(self, 'Error','У вас уже есть это событие', QMessageBox.Ok)
            return

        if type_dv == "Добавить":
            type_dv, ok_pressed = QInputDialog.getText(self, "Название", "Введите название типа")
            if ok_pressed:
                add_type = '''
                INSERT INTO types(name) VALUES(?)
                '''

                self.cursor.execute(add_type, (type_dv,))
                self.con.commit()
                self.comboBox_type.addItem(type_dv)

        while name == "":   
            name, ok_pressed = QInputDialog.getText(self, "Название", "Введите название заметки")
            if not ok_pressed:
                return
                break
        query = '''
            INSERT INTO development(name_db, time_db, data_db, else_db, type_db) VALUES(?, ?, ?, ?, 
                (SELECT id FROM types
                    WHERE name = ?))
            '''
        self.cursor.execute(query, (name, time, data, text_else, type_dv))
        self.con.commit()
        self.line_name.clear()
        self.plainTextEdit_else.clear()



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
