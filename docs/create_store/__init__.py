"""
Random store generator!
""" 

from parse.apps.stores.models import Store, Settings, Subscription

class RandomStoreGenerator(object):

    def __init__(self):
        # TODO load resources
        pass
        
    def create_random_store(self):
        # TODO
        pass
        
        
if __name__ == "__main__":
    generator = RandomStoreGenerator()
    for i in range(1):
        generator.create_random_store()
