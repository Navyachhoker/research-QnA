#Responsible for displaying output to the terminal


def print_answer(answer: str):

    print()

    print("=" * 70)

    print("ANSWER")

    print("=" * 70)

    print(answer)

    print()


def print_sources(sources):

    print("=" * 70)

    print("SOURCES")

    print("=" * 70)

    print()

    for source in sources:

        print(
            f"[Source {source['source_num']}] "
            f"{source['paper']} "
            f"(Page {source['page']})"
        )

        print(source["snippet"])

        print()


def print_papers(papers):

    if not papers:

        print(
            "\nNo papers have been ingested.\n"
        )

        return

    print()

    print("=" * 70)

    print("INGESTED PAPERS")

    print("=" * 70)

    for paper in papers:

        print(f"• {paper}")

    print()


def print_error(message):

    print()

    print(f"ERROR: {message}")

    print()