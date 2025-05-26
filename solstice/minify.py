# pyright: reportMissingImports=false, reportMissingModuleSource=false

from minify_html import minify


def minify_html(contents: str) -> str:
	return minify(
		contents,
		minify_js=True,
		minify_css=True,
		remove_processing_instructions=True,
		allow_removing_spaces_between_attributes=True,
		allow_optimal_entities=True,
	)
