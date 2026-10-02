from thin_helper.output_check import check_reconstruction, clean_reconstruction, rejected, trim_trailing_chatter
from thin_helper.reconstruct_coordinator import ReconstructCoordinator

MEMORY = "We sat on the porch and counted the seconds between lightning and thunder."


def test_clean_memory_has_no_flags():
    assert check_reconstruction(MEMORY) == []


def test_empty_and_star_only_are_rejected():
    assert rejected(check_reconstruction(""))
    assert rejected(check_reconstruction("***** ***"))


def test_prompt_echo_and_task_talk_are_rejected():
    echo = "Do one last quiet pass over the whole thing. Clean up the flow and meaning."
    assert "prompt_echo" in check_reconstruction(echo)
    assert "meta_commentary" in check_reconstruction("The Smart Robot felt the sand.")
    assert rejected(check_reconstruction("I'm sorry, but I can't help with that."))


def test_marker_leak_is_rejected():
    assert "marker_leak" in check_reconstruction("=== FINAL FUZZ ===\n*a*b")


def test_residual_fuzz_is_info_only():
    codes = check_reconstruction("W* s*t on the p*rch ** *** ***** ****")
    assert "residual_fuzz" in codes
    assert not rejected(codes)


def test_trailing_chatter_is_trimmed():
    text = MEMORY + "\n\nThis reconstruction is a best guess with Quiet Rewrite changes."
    assert trim_trailing_chatter(text) == MEMORY
    assert trim_trailing_chatter(MEMORY + "\n\n" + MEMORY) == MEMORY


def test_parser_tolerates_split_markers_and_falls_back_to_step4():
    raw = "===\nSTEP 1 ===\na\n\n===\nSTEP 4 ===\n" + MEMORY
    parsed = ReconstructCoordinator().parse_reconstruction(raw)
    assert parsed["reconstructed_memory"] == MEMORY
    memory, flags = clean_reconstruction(parsed)
    assert memory == MEMORY and "from_step4" in flags


def test_parser_last_final_wins():
    raw = "=== RECONSTRUCTED MEMORY ===\nold\n\n=== STEP 4 ===\nx\n\n=== RECONSTRUCTED MEMORY ===\n" + MEMORY
    assert ReconstructCoordinator().parse_reconstruction(raw)["reconstructed_memory"] == MEMORY


def test_coordinator_blanks_rejected_output():
    coord = ReconstructCoordinator(model_caller=lambda p: "=== STEP 4 ===\n[full text after step 4]\n\n"
                                   "=== RECONSTRUCTED MEMORY ===\nThe Smart Robot used Creative Guessing.")
    out = coord.reconstruct_from_fight_end({"final_fuzz": "*a*", "fresh_clues": []})
    assert out["reconstructed_memory"] == ""
    assert "meta_commentary" in out["quality_flags"]


def test_parser_handles_non_string():
    assert ReconstructCoordinator().parse_reconstruction(None) == {"reconstructed_memory": ""}
