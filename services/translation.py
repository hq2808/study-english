from deep_translator import GoogleTranslator

def translate_text(text, source='en', target='vi'):
    try:
        translator = GoogleTranslator(source=source, target=target)
        translation = translator.translate(text)
        return translation
    except Exception as e:
        raise e
