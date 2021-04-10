const tapContainer = document.querySelector('.about');
const flex_Container = document.querySelectorAll('.contents_container');
const taps = document.querySelectorAll('.about > span');


function changeMenu(e){
    let elem = e.target;
    
    for (var i = 0; i < flex_Container.length; i++) {
        flex_Container[i].classList.remove('active');
        taps[i].classList.remove('on');
    }
    
    if(elem.matches('[class="my_post"]')){
        
        flex_Container[0].classList.add('active');
        taps[0].classList.add('on');
        
    }else if(elem.matches('[class="book_mark"]')){
        
        flex_Container[1].classList.add('active');
        taps[1].classList.add('on');
        
    }
    
}


tapContainer.addEventListener('click', changeMenu);


/*
결과적으로 active와 on은 사용자가 인식하기 위해서 만든 보이기위한용일뿐(css용)
실질적으로는 taps에서 몇번째 배열을 list에 넣느냐에 따라 나오는 값이 내 포스트와 북마크로 바뀌는 것임
.active는 profile.css에서 볼 수 있음 

*/