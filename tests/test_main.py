from fabricflow.main import main


def test_main():
    import io
    import contextlib

    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        main()

    # Check if the output is as expected
    assert captured_output.getvalue().strip() == "Welcome to FabricFlow!", (
        "Output did not match expected value."
    )
