from rapidfuzz import fuzz
import pandas as pd


def talker_file_loader() -> pd.DataFrame:
    df = pd.read_csv(filepath_or_buffer="statics/dialogues.txt", encoding="utf-8", delimiter=";", index_col=False,
                     names=["phrase"], header=None)
    df["phrase"] = df["phrase"].astype(str)
    return df


talker_phrases = talker_file_loader()


def talker_answer(text: str) -> str:
    text = text.strip()
    talker_phrases["token_set_ratio"] = talker_phrases.apply(
        lambda x: fuzz.token_set_ratio(x["phrase"], text),
        axis=1)
    compare_value = 100
    next_phrase = None
    while compare_value > 50:
        maxim = talker_phrases.loc[talker_phrases["token_set_ratio"] >= compare_value]
        if not maxim.empty:
            try:
                founded_item = maxim.sample()
                founded_index = founded_item.index.values.astype(int)[0]
                next_phrase = talker_phrases.iloc[[founded_index + 1]]["phrase"].item()
                break
            except Exception as e:
                print(e)
        compare_value -= 5
    return next_phrase or "Не знаю, что и сказать"
