def prettify_matches(matches: list) -> str:
    if matches:
        output = ""
        for number, match in enumerate(matches):
            output += f"Match number: {number + 1}\n"
            for key, value in match.items():
                    output += f"{key}: {value}\n"
            output += "\n"
        return output
    else:
        return "No matches found."
