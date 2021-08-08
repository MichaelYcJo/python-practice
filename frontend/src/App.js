import 'App.scss';
import { BrowserRouter } from 'react-router-dom';
import { AppProvider } from 'store';
import "antd/dist/antd.css"

import Root from 'pages'

function App() {
  return (
    <div>
      <AppProvider>
        <BrowserRouter>
          <Root />
        </BrowserRouter>
      </AppProvider>
    </div>
  );
}

export default App;
