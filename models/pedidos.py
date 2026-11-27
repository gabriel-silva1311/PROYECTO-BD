from datetime import datetime
class Pedido :
    def __init__(self,items, total):
     self.items = items;
     self.total=total;
     self.feha_hora=datetime.now();
     self.estado='pendiente'; 
    def toDbConnection(self): 
     return {
            "items": self.items,
            "total": self.total,
            "fecha_hora": self.fecha_hora,
            "estado": self.estado,
        }    