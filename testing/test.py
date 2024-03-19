
from PyQt6.QtWidgets import QApplication
import unittest
from unittest.mock import MagicMock, patch
import sys, os



project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_path)


from UI.login import LoginWindow  # Now import your module

class TestLoginWindow(unittest.TestCase):

    def setUp(self):
        # We mock the success_callback to test if it's called correctly.
        self.success_callback = MagicMock()
        self.login_window = LoginWindow(success_callback=self.success_callback)

    # Bepatchelni hogy megtalálja a login csomagot
    @patch('UI.login.sqlite3')

    
    
    def test_login_success(self, mock_sqlite):
        # Set up the mock for a successful login
        mock_cursor = mock_sqlite.connect().cursor()
        mock_cursor.fetchone.return_value = [b'stored_password_hash']
        
        # You'd replace 'stored_password_hash' and 'correct_password' with actual hashed values and test passwords.
        with patch('UI.login.check_password') as mock_check_password:
            mock_check_password.return_value = True
            self.login_window.username_input.setText('Sikos Mark')
            self.login_window.password_input.setText('Neaddfel2')
            self.login_window.on_login_clicked()

            # Verify that the success callback was called
            self.success_callback.assert_called_once()

    
    
    @patch('UI.login.sqlite3')
    def test_login_wrong_password(self, mock_sqlite):
        mock_cursor = mock_sqlite.connect().cursor()
        mock_cursor.fetchone.return_value = [b'stored_password_hash']

        with patch('UI.login.check_password') as mock_check_password:
            mock_check_password.return_value = False
            self.login_window.username_input.setText('Sikos Mark')
            self.login_window.password_input.setText('wrong_password')
            self.login_window.on_login_clicked()

            # The success callback should not be called
            self.success_callback.assert_not_called()

    @patch('UI.login.sqlite3')
    def test_login_wrong_username(self, mock_sqlite):
        mock_cursor = mock_sqlite.connect().cursor()
        mock_cursor.fetchone.return_value = None  # No user found

        with patch('UI.login.check_password') as mock_check_password:
            # The check_password function should not be called, but let's set it to return True
            mock_check_password.return_value = True
            self.login_window.username_input.setText('wrong_username')
            self.login_window.password_input.setText('Neaddfel2')
            self.login_window.on_login_clicked()

            # The success callback should not be called
            self.success_callback.assert_not_called()

    @patch('UI.login.sqlite3')
    def test_login_wrong_username_and_wrong_password(self, mock_sqlite):
        mock_cursor = mock_sqlite.connect().cursor()
        mock_cursor.fetchone.return_value = None  # No user found

        with patch('UI.login.check_password') as mock_check_password:
            # Even if we set check_password to return True, it should not be called due to no user found
            mock_check_password.return_value = True
            self.login_window.username_input.setText('wrong_username')
            self.login_window.password_input.setText('wrong_password')
            self.login_window.on_login_clicked()

            # The success callback should not be called
            self.success_callback.assert_not_called()

if __name__ == '__main__':
    app = QApplication(sys.argv)  # Create a QApplication instance
    unittest.main()
