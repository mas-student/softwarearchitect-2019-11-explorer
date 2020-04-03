import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import {observable} from "mobx";


const chain = observable({ number: -1 })
function increase() {
  chain.number = chain.number + 1
}

it('renders without crashing', () => {
  const div = document.createElement('div');
  ReactDOM.render(<App chain = {chain} increase = {increase}/>, div);
});
