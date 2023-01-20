from typing import Dict
from ..lib.server import Server
from ..lib.client import Client
from ..utils import get_logger

class MTFLEnv:
    def __init__(self, server: Server, clients: Dict[int, Client], communication_rounds:int, n_clients: int, sample_rate:float) -> None:
        """_summary_

        Args:
            server (Server): _description_
            clients (List[Client]): _description_
            communication_rounds (int): _description_
        """
        super().__init__()
        self.server = server
        self.clients = clients
        self.communication_rounds = communication_rounds
        
        self.n_clients = n_clients
        self.sample_rate = sample_rate
        self.logger = get_logger()


    #Todo initialize by configuration
    def init_config(self) -> None:
        pass

    # TODO initilize server
    def init_server(self) -> None:
        pass
    
    # TODO initilize clients
    def init_clients(self) -> None:
        pass


    def run(self,local_epochs):
        
        for round in range(self.communication_rounds):
            selected = self.server.client_sample(n_clients= self.n_clients, sample_rate=self.sample_rate)
            
            globa_encoder = self.server.get_global_model_params()
            
            nets_encoders = []
            local_datasize = []
            accuracies = []
            self.logger.info('*******starting rounds %s optimization******' % str(round+1))

            for id in selected:
                self.logger.info('optimize the %s-th clients' % str(id))
                client = self.clients[id]
                if id != client.id:
                    raise IndexError("id not match")
                
                client.set_model_params(globa_encoder, module_name="encoder")
                client.client_update( epochs=local_epochs)
                accuracy = client.eval()["test_accuracy"]
                accuracies.append(accuracy)
                
                nets_encoders.append(client.get_model_params(module_name="encoder"))
                local_datasize.append(client.datasize)

            self.server.server_update(nets_encoders=nets_encoders, local_datasize=local_datasize,globa_encoder= globa_encoder)
            self.logger.info('Global accuracy: {:.3f}'.format(sum(accuracies)/len(accuracies)))
            #Cannot call server.eval() since global model has no predictor/decoder head
            #self.server.eval()
