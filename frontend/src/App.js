import 'App.scss';
import { BrowserRouter } from 'react-router-dom';
import "antd/dist/antd.css"

import Root from 'pages'

function App() {
  return (
    <div>
      <BrowserRouter>
        <Root />
      </BrowserRouter>
    </div>
  );
}

export default App;
