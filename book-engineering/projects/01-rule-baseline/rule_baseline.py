# A teaching baseline, not a security filter.
KEYWORDS = ("برنده جایزه", "رمز عبور")


def classify(message):
    """True means flag the message for human review."""
    text = message.strip()
    return any(word in text for word in KEYWORDS)


def main():
    cases = [
        ("شما برنده جایزه شدید", True),
        ("رمز عبور خود را ارسال کنید", True),
        ("فردا جلسه داریم", False),
        ("این درس درباره امنیت رمز عبور است", False),
        ("برای دریافت پاداش، اطلاعات بانکی بدهید", True),
    ]
    correct = 0
    for text, expected in cases:
        predicted = classify(text)
        correct += predicted == expected
        print(f"prediction={predicted}, expected={expected}: {text}")
    print(f"accuracy={correct}/{len(cases)} = {correct/len(cases):.0%}")


if __name__ == "__main__":
    main()
