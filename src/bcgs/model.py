import torch
import torch.nn.functional as F
from torch_geometric.nn import GATConv, global_max_pool
from torch.nn import LayerNorm

"""
Enhanced GAT：使用Transformer风格的GAT，结合残差连接和层归一化
- 使用多头注意力机制
- 添加残差连接
- 使用层归一化
- 使用最大池化而不是平均池化
- 添加跳跃连接以缓解过平滑
"""

class GATLayer(torch.nn.Module):
    def __init__(self, in_channels, out_channels, heads=4, dropout=0.2, concat=True):
        super(GATLayer, self).__init__()
        self.gat = GATConv(in_channels, out_channels, heads=heads, 
                          dropout=dropout, concat=concat)
        # 如果concat=True，实际输出维度是 out_channels * heads
        self.norm = LayerNorm(out_channels * heads if concat else out_channels)
        self.dropout = dropout
        self.in_channels = in_channels
        self.out_channels = out_channels * heads if concat else out_channels

        # 如果输入输出维度不同，使用线性变换进行残差连接
        if self.in_channels != self.out_channels:
            self.residual = torch.nn.Linear(in_channels, self.out_channels)
        else:
            self.residual = torch.nn.Identity()

    def forward(self, x, edge_index):
        # 主路径
        out = self.gat(x, edge_index)
        out = F.elu(out)
        out = F.dropout(out, p=self.dropout, training=self.training)
        
        # 残差连接
        res = self.residual(x)
        out = out + res
        
        # 层归一化
        out = self.norm(out)
        
        return out

class GCN(torch.nn.Module):
    def __init__(self, num_node_features, hidden_channels=64, heads=4):
        super(GCN, self).__init__()
        
        # 第一层GAT
        self.conv1 = GATLayer(
            in_channels=num_node_features,
            out_channels=hidden_channels,
            heads=heads,
            dropout=0.2,
            concat=True
        )
        
        # 第二层GAT
        self.conv2 = GATLayer(
            in_channels=hidden_channels * heads,
            out_channels=hidden_channels,
            heads=heads,
            dropout=0.2,
            concat=True
        )
        
        # 输出层
        self.output_layer = torch.nn.Sequential(
            torch.nn.Linear(hidden_channels * heads, hidden_channels),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.2),
            torch.nn.Linear(hidden_channels, 1)
        )

    def forward(self, x, edge_index, batch):
        # 第一层GAT
        x1 = self.conv1(x, edge_index)
        
        # 第二层GAT
        x2 = self.conv2(x1, edge_index)
        
        # 跳跃连接：结合两层的特征
        x = x1 + x2
        
        # 全局最大池化
        x = global_max_pool(x, batch)
        
        # 输出层
        x = self.output_layer(x)
        
        return x