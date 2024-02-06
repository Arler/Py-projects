from django import template


register = template.Library()


@register.filter()
def censor(text, word):
	if isinstance(text, str):
		if word in text:
			length_censored = '*' * len(word[1:])
			censored_word = word.replace(word[1:], length_censored)
			text = text.replace(word, censored_word)
		return text
	else:
		raise ValueError(f'Неправильный тип данных {type(text)}')
