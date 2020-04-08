import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import './index.css';

import { observable, computed, decorate } from "mobx"


class ObservableWalletStore {
    loading = false;
	wallets = [];
	balances_by_address = {};

    get balanced() {
        return this.wallets.map(wallet => {
            let balanced = Object.assign({}, wallet);
            balanced.balance = this.balances_by_address[balanced.address];
            return balanced
        });
	}

	fetch() {
        this.wallets.length = 0;
        this.loading = true;
        fetch('http://localhost:3000/wallets').then(response => response.json()).then(data => {
            console.log('fetched wallets', data);
            this.loading = false;
            data.forEach(wallet => {
                this.wallets.push(wallet);
                this.balances_by_address[wallet.address] = wallet.balance || 0;
            });
        });
    }
}

decorate(ObservableWalletStore, {
    wallets: observable,
    loading: observable,
    balanced: computed,
    balances_by_address: observable,
});

const observableWalletStore = new ObservableWalletStore();
const chain = observable({ number: -1 });
let globals = {app: null};

const app = <App
    store={observableWalletStore}
    chain={chain}
    globals={globals}
/>;

window.socket = undefined;

function init_socket() {
    const result = new WebSocket('ws://localhost:3000/ws');
    console.log('web socket inited', result);
    return result;
}

function setup_socket(socket) {
    window.socket.addEventListener('open', function (event) {
        window.socket.send('Hello Server!');
    });

    window.socket.addEventListener('message', function (event) {
        console.log('Message from server ', event.data);
        const data = JSON.parse(event.data)

        observableWalletStore.balances_by_address[data.address] = data.balance
    });

    window.socket.addEventListener('close', function (event) {
        console.log('Good buy Cruel Server!');
        window.socket = init_socket();
        setup_socket(window.socket);
    });

    console.log('web socket set up', socket);
}

window.socket = init_socket();
setup_socket(window.socket);

ReactDOM.render(
  app, document.getElementById('root')
);
