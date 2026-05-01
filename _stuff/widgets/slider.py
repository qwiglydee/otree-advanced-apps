from otree.forms.widgets import IntegerWidget


class IntegerSlider(IntegerWidget):
    """Slider widget"""

    def get_html_fragments(self):
        attrs = self.attrs()
        yield f"""<input type="range" class="form-range" {attrs}>"""
