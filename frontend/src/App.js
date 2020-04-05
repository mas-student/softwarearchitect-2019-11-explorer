import React, {Component} from 'react';
import logo from './logo.svg';
import './App.css';
import {observer} from "mobx-react"


function Wallet(props) {
    return <p>На счету {props.address} имеется <span id={props.address}>{props.balance}</span> единиц</p>
}


const App = observer(
    class App extends Component {
        constructor(props) {
            super(props);
            this.state = {
                loggedIn: false,
                email: "",
                wallets: null,
                session_id: null,
                adding: false
            };

            props.globals.app = this;
        }

        signup() {
            const email = prompt('Введите электронный адрес для регистрации');
            const password = prompt('Введите пароль для регистрации');
            const data = {email, password};

            if (!email || !password) {
                alert(`Требуется ввести и электронный адрес и пароль`);
                return
            }

            fetch(
                'http://localhost:3000/signup',
                {method: 'POST', body: JSON.stringify(data)}
                )
                .then(response => response.json())
                .then(data => {
                    console.log(`Signing up succeeded with ${JSON.stringify(data)}`);
                })
                .catch(err => {
                    alert(`Регистрация выполнилась с ошибкой ${JSON.stringify(err)}`)
                });
        }

        signin() {
            const email = prompt('Введите электронный адрес для входа');
            const password = prompt('Введите пароль для входа');
            const data = {email, password};

            if (!email || !password) {
                alert(`Требуется ввести и электронный адрес и пароль`);
                return
            }

            fetch(
                'http://localhost:3000/signin',
                {method: 'POST', body: JSON.stringify(data)}
                )
                .then(response => {
                    if (response.status === 401) {
                        return response.text().then(err => {
                             alert(`Вход выполнился с ошибкой ${JSON.stringify(err)}`);
                        })
                    } else if (response.status === 200) {
                        return response.json().then(data => {
                            JSON.stringify()
                            console.log(`Signing in succeeded with ${JSON.stringify(data)}`);
                            this.setState({session_id: data.session_id});
                            this.setState({email: data.email});
                            this.setState({loggedIn: true});
                            this.props.store.fetch();
                        })
                     } else {
                        alert(`Unknown status ${response.status}`);
                    }
                })
        }

        createWallet() {
            const session_id = this.state.session_id;
            const address = prompt('Введите адрес кошелька');

            console.log(`Creating wallet ${address}`);

            const data = {session_id, address};
            this.setState({adding: true});
            fetch(
                'http://localhost:3000/wallets',
                {method: 'POST', body: JSON.stringify(data)}
                )
                .then(response => response.json())
                .then(data => {
                    console.log(`Creating wallet succeeded with ${JSON.stringify(data)}`);
                    this.setState({adding: false});
                    this.props.store.fetch();
                })
                .catch(err => {
                    this.setState({adding: false});
                    alert(`Creating wallet failed with ${JSON.stringify(err)}`)
                });
        }

        render() {
            const loading = this.props.store.loading;
            const adding = this.state.adding;
            const wallets = this.props.store.balanced;

            return (
                <div className="App">
                    <div className="App-header">
                        <img src={logo} className="App-logo" alt="logo"/>
                        <h2>Добро пожаловать в обозреватель цепочки блоков</h2>
                    </div>
                    {!this.state.loggedIn
                        ?<div>
                            <p>Вы ещё не вошли</p>
                            <button onClick={() => this.signin()}>Войти</button>
                            <button onClick={() => this.signup()}>Зарегистрироваться</button>
                        </div>
                        :<div>
                            <p>Вы вошли c электронным адресом {this.state.email + " "}
                                и ваш сессионный идентификатор {this.state.session_id}
                            </p>
                            {loading
                                ? <span>Получение кошельков...</span>
                                : <div>
                                    {adding
                                        ? <span>Добавление кошелька...</span>
                                        : <span></span>
                                    }
                                    <p>У вас добавлено {wallets.length} кошельков</p>
                                    <button onClick={() => this.createWallet()}>Добавить кошелек</button>

                                    {wallets && wallets.map(wallet =>
                                        <Wallet key={wallet.id} address={wallet.address} balance={wallet.balance}/>)
                                    }
                                </div>
                            }
                        </div>
                    }
                </div>
            );
        }
    }
);

export default App;
