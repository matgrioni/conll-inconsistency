def has_flags(args, *flags):
    return reduce(lambda acc, option: acc or option in args, flags, False)
