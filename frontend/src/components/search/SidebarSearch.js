
import React, {useState } from 'react'
import { useRecoilState } from 'recoil';
import { productQueryState } from 'recoil/productRecoil';
import { useHistory } from 'react-router-dom'


const SidebarSearch = () => {

  const [word, setWord] = useState("");
  const [queryState, setQueryState] = useRecoilState(productQueryState);

  let history = useHistory()
  

  const searchProduct = (e) =>{
      e.preventDefault();
      setQueryState(word)
      if (queryState) {
          history.push(`/products/search`)
      } else {
          history.push(history.push(history.location.pathname))
      }

  }

  return (
    <div className="sidebar-widget">
      <h4 className="pro-sidebar-title">Search </h4>
      <div className="pro-sidebar-search mb-50 mt-25">
        <form className="pro-sidebar-search-form" action="#">
          <input type="text" placeholder="Search here..." onChange= { (e) => setWord(e.target.value)} />
          <button  onClick={searchProduct}>
            <i className="pe-7s-search" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default SidebarSearch;
