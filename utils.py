def italics(string):
    return "_{}_".format(string)


def bold(string):
    return "*{}*".format(string)


def format_definitions(word_data):
    message = "{}\n".format(bold("Definitions"))
    for definition in word_data["definitions"]:
        def_string = "{} : {}".format(
            italics(definition.partOfSpeech), definition.text
        )
        message += "{}\n\n".format(def_string)
    return message


def format_example(word_data):
    if not word_data["example"]:
        return "No example found"
    message = "{}\n".format(bold("Example"))
    message += "{}\n\n".format(word_data["example"].text)
    return message


def format_synonyms(word_data):
    if not word_data["synonyms"]:
        return "No synonyms found"
    message = "{}\n".format(bold("Synonyms"))
    for synonym in word_data["synonyms"]:
        message += "{}\n".format(synonym)
    return message


def format_antonyms(word_data):
    if not word_data["antonyms"]:
        return "No antonyms found"
    message = "{}\n".format(bold("Antonyms"))
    for antonym in word_data["antonyms"]:
        message += "{}\n".format(antonym)
    return message


def format_urbandictionary(word_data):
    message = "{}\n{}\n\n{}\n{}".format(
        bold("Definition"),
        word_data["definition"],
        bold("Example"),
        word_data["example"],
    )
    return message
