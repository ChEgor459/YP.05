import json
import os

FILE = "stats.json"
SETTINGS_FILE = "settings.json"


def load():
    return json.load(open(FILE, encoding="utf-8")) if os.path.exists(FILE) else {}


def save(data):
    json.dump(data, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=4)


def update(game, difficulty, win, score, level, moves, language):
    data = load()

    diff_map = {
        "easy": "easy", "medium": "medium", "hard": "hard",
        "Легкий": "easy", "Средний": "medium", "Сложный": "hard",
        "Easy": "easy", "Medium": "medium", "Hard": "hard"
    }
    diff_key = diff_map.get(difficulty, "easy")

    if not data:
        data = {
            "total_games": 0, "training_runs": 0,
            "pairs_total": 0, "sequence_total": 0,
            "audio_total": 0, "changes_total": 0,
            "pairs": {}, "sequence": {}, "audio": {}, "changes": {}
        }

    data.setdefault(game, {})

    if diff_key not in data[game]:
        data[game][diff_key] = (
            {"wins": 0, "losses": 0, "best_score": 0, "best_moves": 0}
            if game == "pairs"
            else {"wins": 0, "losses": 0, "best_level": 0, "best_score": 0}
        )

    data["total_games"] = data.get("total_games", 0) + 1
    total_key = f"{game}_total"
    data[total_key] = data.get(total_key, 0) + 1

    block = data[game][diff_key]
    block["wins" if win else "losses"] = block.get("wins" if win else "losses", 0) + 1

    if game == "pairs":
        best_score = block.get("best_score", 0)
        best_moves = block.get("best_moves", 10 ** 9)

        if (score > best_score) or (score == best_score and moves < best_moves):
            block["best_score"] = score
            block["best_moves"] = moves
    else:
        if level > block.get("best_level", 0):
            block["best_level"], block["best_score"] = level, score

    save(data)
    print(f"DEBUG: Saved {game} {diff_key} - score:{score}")


def load_settings():
    return json.load(open(SETTINGS_FILE, encoding="utf-8")) if os.path.exists(SETTINGS_FILE) else {
        "language": "Русский",
        "sound_on": True
    }


def save_settings(language, sound_on):
    json.dump({"language": language, "sound_on": sound_on},
              open(SETTINGS_FILE, "w", encoding="utf-8"),
              ensure_ascii=False, indent=4)