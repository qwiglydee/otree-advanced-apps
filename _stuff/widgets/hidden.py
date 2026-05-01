from otree.forms.widgets import BaseWidget


class HiddenWidget(BaseWidget):
    """Widget to make hidden form fields
    Note: rendering with {{ formfields }} still inserts blank spaces around the field
    """

    def get_html_fragments(self):
        attrs = self.attrs()
        yield f"""<input type="hidden" {attrs}>"""
