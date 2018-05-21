def gen_key(params):
    metrics = params.get('metrics')
    tags = params.get('tags')
    key_ = metrics + str(tags)
    return hash(key_)
