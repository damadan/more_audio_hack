def apply_punctuation(text: str, lang: str) -> str:
    return text


def apply_itn(text: str, lang: str) -> str:
    return text


def postprocess_event(ev, lang: str):
    txt = ev.revised_text or ev.text
    txt = apply_punctuation(txt, lang)
    txt = apply_itn(txt, lang)
    if ev.revised_text is not None:
        ev = ev.model_copy(update={"revised_text": txt})
    else:
        ev = ev.model_copy(update={"text": txt})
    return ev
