import re
from typing import Sequence

# primmitive regex fuzzy matching. not very good for large collections
def fuzzy_match_result(input: str, collection: Sequence) -> list[str]:
	text = "".join(input.split())
	text = text.lower()
	pattern = ".*?".join(text)
	regex = re.compile(pattern)
	suggestions = []
	for item in collection:
		match = regex.search(item.lower())
		if match:
			suggestions.append((len(match.group()), match.start(), item))
	return [x for _,_,x in sorted(suggestions)]
