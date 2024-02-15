// React stuff
import React, { useEffect, useState } from 'react';
import { Player, ControlBar } from 'video-react';
import toast, { Toaster } from 'react-hot-toast';
import Card from './Components/Card';

// Icons
import { FaHome, FaGithub, FaLinkedin } from "react-icons/fa";
import { AiFillCode } from "react-icons/ai";
import { FiX } from "react-icons/fi";

// Effects / Buttons
import Typewriter from 'typewriter-effect';
import FadeLoader from "react-spinners/FadeLoader";
import Hamburger from 'hamburger-react'
import anime from "animejs";

function App() {

  // Used for word array construction
  const [storyArray, setStoryArray] = useState(null);
  const [currentWord, setCurrentWord] = useState(1); // Default to the first word after story type
  const [userId, setUserId] = useState('UID');

  // Buttons Stuff
  const [isSubmit, setIsSubmit] = useState(false);
  const [newWordLoading, setNewWordLoading] = useState(false);

  const [videoSrc, setVideoSrc] = useState("./video/placeholder.mp4");
  const [isLoading, setIsLoading] = useState(false);

  // Runs on startup.
  useEffect(()=> {
    anime({
      targets: '.card_list',
      translateY: 10,
      opacity: 100,
      delay: anime.stagger(250)
    });

    setUserId(generateRandomString())
  }, []);

  // ###### HELPER FUNCTIONS ###### //

  //Generates random user ID
  function generateRandomString() {
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
      let randomString = '';
      for (let i = 0; i < 6; i++) {
        randomString += characters.charAt(Math.floor(Math.random() * characters.length));
      }
      return randomString;
  };

  // Time out for error handling
  function timeout(delay) {
    return new Promise( res => setTimeout(res, delay) );
  };

  // Moves "currentWord" state up by 1, replaces that index with whatever is in the input field.
  const tickCurrentWord = (array) => {
    const wordElement = document.querySelector('.word-list p');
    wordElement.textContent = array[currentWord];
    setCurrentWord(currentWord + 1)
  };

  // ###### API REQUESTS ###### //

  // Fetches video from Flask API
  const generateVideo = () => {
    return new Promise((resolve, reject) => {
      if (storyArray) {
        setIsLoading(true); // Loading must be set to true

        anime({
          targets: '.loading-screen',
          opacity: 100,
          duration: 3000,
          easing: 'easeInCubic'
        });

        fetch('http://localhost:5000/generate-video', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            strings: storyArray,
          }),
        })
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.blob();
        })
        .then(blob => {
          // Create a URL for the video blob
          console.log(blob)
          const url = window.URL.createObjectURL(blob);
          setVideoSrc(url); // Update state with the generated video URL

          // Automatically download the video
          const a = document.createElement('a');
          a.href = url;
          a.download = 'AI_Jumble.mp4'; // TODO: Automatic file names?
          a.style.display = 'none';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);

          cleanupBackend(userId); // We ask the back end to delete its instance of the video.

          anime({
            targets: '.loading-screen',
            opacity: 100,
            duration: 3000,
            easing: 'easeInCubic',
            complete: setIsLoading(false),
          });
          resolve(); // Resolve the promise once video generation is complete
        })
        .catch(error => {
          console.error('Error:', error);
          reject(error); // Reject the promise if an error occurs
        });
      }
    });
  };

  // Grabs script from back end, initiates specific story on the front end based on that script.
  const startStory = (newStoryType, storyTitle) => {
    const storyTitleElement = document.querySelector('.story-title');
    storyTitleElement.textContent = storyTitle;

    // Make a GET request to the Flask API endpoint for story information.
    fetch(`http://localhost:5000/generate-array?input_string=${newStoryType}`)
        .then(response => {
            // Check if the response is successful
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json(); // Parse the JSON response
        })
        .then(data => {
            setStoryArray(data.script); // Set the entire array to state
            console.log("Return results: ", data.script); // Log the entire array
            // setStoryType(data.script[0]);
            tickCurrentWord(data.script); // We want to start on the first word, not the story type.

            anime({
                targets: '.main-menu',
                translateX: -1500,
                opacity: 0,
                height: "80vh",
                easing: 'easeOutCubic'
            });

            anime({
                targets: '.story-menu',
                top: 10,
                easing: 'easeOutCubic'
            });
        })
        .catch(error => {
            setStoryArray(null); // Clear array result
            console.error('Error:', error);
            toast.error("AI Jumbles is having some trouble. Try again later!");
        });
  };

  // Deletes backend instance of a video based on the userId after the video has been returned locally to the user.
  const cleanupBackend = async () => {
    try {
      const response = await fetch('http://localhost:5000/cleanup-usercode', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId
        })
      });

      if (response.ok) {
        // Request was successful
        console.log('User code cleaned up successfully');
      } else {
        // Request failed
        const errorMessage = await response.text();
        console.error('Error:', errorMessage);
      }
    } catch (error) {
      // Request failed due to network error or other reasons
      console.error('Error:', error.message);
    }
  };
  
  // ###### WORD SUBMISSION FUNCTIONS ######
  
  // Submits word list and initiates video generation on the back end.
  const submit = async () => {
    const inputField = document.getElementById('word-input');
    tickCurrentWord(storyArray);
    storyArray[currentWord-1] = inputField.value;
    console.log("Submitting: " + storyArray)

    anime({
      targets: '.story-menu',
      translateX: -1000,
      opacity: 0,
      easing: 'easeOutCubic'
    });

    try{
      await generateVideo(); // Actually Generate the video! Then animate the screen.
      anime({
        targets: '.display-menu',
        top: 10,
        easing: 'easeOutCubic'
      });
    } catch(e) {
      toast.error("Something went wrong... This page will reload");
      await timeout(3000) // Wait 3 seconds
      window.location.href = '/';
    }
    
  };

  // Submits current word, does input validation and initiates the next word.
  const nextWord = () => {
    const wordElement = document.querySelector('.word-list p');
    const inputField = document.getElementById('word-input');

    if(inputField.value === ''){
      //Shake animation
      anime({
        targets: '.word-menu',
        easing: 'easeInOutSine',
        duration: 550,
        translateX: [
          {value: 16 * -1,},{value: 16,},{value: 16/-2,},{value: 16/2,},{ value: 0,}
        ],
      });
    } else {
      setNewWordLoading(true)
      if(wordElement){
        anime({
          targets: '.word-menu',
          opacity: 0,
          easing: 'easeOutCubic',
        });

        anime({
          targets: '.word-menu',
          translateX: -100,
          easing: 'easeOutCubic',
          complete: function(a) {
              // Check if the element exists
            if (wordElement) {
              // Update the text content to "Noun"
              if(currentWord <= storyArray.length-1){
                if(currentWord === storyArray.length-1)  {
                  //Change button on last word to submit.
                  setIsSubmit(true);
                  const submitButton = document.querySelector('.next-button');
                  submitButton.textContent = "Submit Words"
                }
                //Increase current word int
                tickCurrentWord(storyArray);
                storyArray[currentWord-1] = inputField.value;
                console.log(storyArray);
                inputField.value = '';
              } 

              // New input field animation
              anime({
                targets: '.word-menu',
                translateX: 200,
                easing: 'steps(1)',
              });
          
              anime({
                targets: '.word-menu',
                opacity: 100,
                easing: 'easeInCubic',
                complete: function () {
                  setNewWordLoading(false)
                }
              });
          
              anime({
                targets: '.word-menu',
                translateX: 0,
                easing: 'easeInOutCubic',
                complete: function () {
                  setNewWordLoading(false)
                }
              });

              // For Debugging....
              // console.log(currentWord + " : " + storyArray.length)
            }
          }
        });
      }
    }
  };

  // This function is responsible for handling word inputs.
  const handleInputButton = () => {
    console.log(newWordLoading)
    if(!newWordLoading){
      if(isSubmit){
        submit();
      } else {
        nextWord();
      }
    }
  };


  return (
    <div>
      {/* Header */}
      <div className="background"></div>

      {/* Toast for Error Messages */}
      <div><Toaster position="bottom-center" /></div>

      {/* Header */}
      <div className="header">
        <Hamburger size={25} className="hamburger" onToggle={toggled => {
          if (toggled) {
            anime({
              targets: '.side-bar',
              left: -20,
              easing: 'easeOutCubic'
            });
            anime({
              begin: function(anim) {},
              targets: '.background',
              opacity: 1,
              duration: 200,
              easing: 'easeOutCubic'
            });
          } else {
            anime({
              begin: function(anim) {},
              targets: '.background',
              opacity: 0,
              duration: 200,
              easing: 'easeInCubic'
            });
            anime({
              targets: '.side-bar',
              left: -500,
              easing: 'easeOutCubic'
            });
          }
        }} />
        <h1 className="logo">AI Jumbles</h1>
        <div className="empty"></div>
      </div>

      {/* loading indicator */}
      {isLoading ? (
        <div className="loading-screen">
            <div className="loading-content">
              <FadeLoader
                color="white"
                size={150}
                aria-label="Loading Spinner"
                data-testid="loader"
              />
              <Typewriter
                options={{
                  loop: true,
                }}
                onInit={(typewriter) => {
                  typewriter
                    .typeString('Loading...')
                    .pauseFor(2000)
                    .deleteAll()
                    .start();
                }}
              />
            </div>
        </div>
      ) : (
        <div></div>
      )}

      {/* Side Menu */}
      <div className="side-bar">
        <ul>
          <a href="/">
            <li>
              <FaHome />
              <p>Home</p>
            </li>
          </a>
          <a href="https://github.com/hellokugelblitz/AI_Jumbles">
            <li>
              <AiFillCode />
              <p>About This Project</p>
            </li>
          </a>
          <a href="https://github.com/hellokugelblitz">
            <li>
              <FaGithub />
              <p>My Github</p>
            </li>
          </a>
          <a href="https://www.linkedin.com/in/jack-lindsey-noble-55a032254/">
            <li>
              <FaLinkedin />
              <p>My Linkedin</p>
            </li>
          </a>
        </ul>
        <div className="note">
          <p>This project was made with love, by <strong>Jack Noble</strong></p>
          <p>203-349-0236 || jacknoble0303@gmail.com</p>
        </div>
      </div>
    
      {/* Main Menu */}
      <div className="content">
        <div className="main-menu">
          <div className="text-container">
              <Typewriter
                onInit={(typewriter) => {
                  typewriter.changeDelay(80)
                  .typeString('AI Jumbles reinvents your favorite classic word game into something')
                  .typeString('<strong> new.</strong>')
                  .pauseFor(3000)
                  .deleteChars(4)
                  .typeString('<strong> fun.</strong>')
                  .pauseFor(3000)
                  .deleteChars(4)
                  .typeString('<strong> interesting.</strong>')
                  .pauseFor(3000)
                  .deleteChars(12)
                  .typeString('<strong> *adjective*.</strong>')
                  .pauseFor(3000)
                  .deleteChars(12)
                  .typeString('<strong> cool.</strong>')
                  .pauseFor(3000)
                  .deleteChars(5)
                  .typeString('<strong> AI driven.</strong>')
                  .start();
                }}
              />
          </div>
          
          <div className="menu">
              <ul className="card_lists">
                <Card
                  imageSrc="./img/lion.png"
                  title="Nature Documentary"
                  description="Explore the beautiful nature of planet earth with this touching nature documentary."
                  onClick={() => startStory("nature_doc", "Nature Documentary")}
                  isAvailable={true}
                />
                <Card
                  imageSrc="./img/space.png"
                  title="Space Documentary"
                  description="Discover what the other worlds of our universe have to offer, with this exciting space documentary."
                  onClick={() => startStory("space_doc", "Space Documentary")}
                  isAvailable={true}
                />
                <Card
                  imageSrc="./img/office.png"
                  title="Corporate Intro"
                  description="Welcome to your new home. This is the cubicle you will live in for the rest of your life."
                  onClick={() => startStory("corporate_intro", "Corporate Intro")}
                  isAvailable={true}
                />
                <Card
                  imageSrc="./img/cc.jpg"
                  title="Car Commercial"
                  description="Discover what the other worlds of our universe have to offer, with this exciting space documentary."
                  onClick={() => startStory("cc")}
                  isAvailable={false}
                />
                <Card
                  imageSrc="./img/farm.jpg"
                  title="Life on the Farm"
                  description="Discover what the other worlds of our universe have to offer, with this exciting space documentary."
                  onClick={() => startStory("cc")}
                  isAvailable={false}
                />
                <Card
                  imageSrc="./img/tomb.jpg"
                  title="History Channel"
                  description="Discover what the other worlds of our universe have to offer, with this exciting space documentary."
                  onClick={() => startStory("cc")}
                  isAvailable={false}
                />               
              </ul>
          </div>
        </div>

        <div className="story-menu">
          <h1 className="story-title">Nature Documentary</h1>
            <div className="word-menu">
              <div className="word-list">
                  <input autoComplete="off" id="word-input" type="text" name="name" />
                  <p>Submit any Word</p>
              </div>
            </div>
          <button onClick={handleInputButton} className="next-button"> Next Word </button>   
        </div>

        <div className="display-menu">
          <div className="go-back">
            <a href="/">
              <FiX size={25} color={"gray"} />
            </a>
          </div>
          <h1 className="story-title">Your Video:</h1>
          <div className="video-background">
          
            <Player src={videoSrc}>
              <ControlBar autoHide={false} className="my-class" />
            </Player>

          </div>

        </div>  
      
      </div>
    </div>
  );
}

export default App;
