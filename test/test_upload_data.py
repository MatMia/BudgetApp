import src.upload_data as upload_data

class TestXLS:

    test_upload_file = upload_data.importAliorXLS('test/resources/correct_test_upload_file.XLS')

    def test_validate_columns_should_pass_if_correct_file(self):

        column_validation = self.test_upload_file.validate_columns()
        assert column_validation == 'validation_ok'

