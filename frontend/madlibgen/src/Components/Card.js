import React from 'react';

const Card = ({ imageSrc, title, description, onClick, isAvailable}) => {
    
    if(isAvailable){
        return (
            <li className="card_list active" onClick={onClick}>
                <div className="card_listImage">
                    <img src={imageSrc} alt={title} />
                </div>
                <h3 className="card_listTitle">{title}</h3>
                <p className="card_listText">{description}</p>
            </li>
        );
    } else {
        return (
            <li className="card_list old">
               <div className="coming-soon">
                   <h2>COMING SOON</h2>
               </div>
               <div className="card_listImage">
                 <img src={imageSrc} alt={title}/>
               </div>
               <h3 className="card_listTitle">{title}</h3>
               <p className="card_listText">
                {description}
               </p>
             </li>  
        );
    }
};

export default Card;