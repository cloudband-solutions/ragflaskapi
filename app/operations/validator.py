class Validator:
    def __init__(self):
        self.payload = {}
        self.num_errors = 0

    def valid(self):
        return self.num_errors == 0

    def invalid(self):
        return self.num_errors > 0

    def count_errors(self):
        for errs in self.payload.values():
            if not errs:
                continue

            first = errs[0]
            if isinstance(first, str):
                self.num_errors += len(errs)
                continue

            if isinstance(first, dict):
                for err in errs:
                    if not err:
                        continue
                    for entry in err.values():
                        if entry:
                            self.num_errors += len(entry)
