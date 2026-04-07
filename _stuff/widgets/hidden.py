from otree.forms.widgets import BaseWidget


class HiddenWidget(BaseWidget):
    """Just a widget to make hidden form fields"""

    def get_html_fragments(self):
        attrs = self.attrs()
        yield f"""<input type="hidden" {attrs}>"""
