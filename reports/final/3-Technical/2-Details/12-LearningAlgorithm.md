### Learning Algorithm {#sec-3-2-12-2}

#### Introduction {-}

One of the principal goals of the project is allow users to train the system to control their devices without 
creating explicit rules. The Aria system observes the user's interactions with devices and sensors during 
*training sessions*. A training session is a short period of time in which the user performs a series of 
actions that they would like the system to replicate in the future. Actions may include triggering sensors,
or controlling the state of an actuator. Each training session is associated with a particular *behaviour* that
the user is attempting to teach the system. 

From the viewpoint of the Aria system, all user actions and sensor reports during a training session are 
processed as events; these events are either labelled as user actions or sensor reports. The task of the system
is to infer associations between the reported values from sensors and the actions that a user took in response.
This process of inferring the relationship between the state of sensors and user actions is referred to as
*supervised learning* 

An iterative approach was used for development of the supervised learning component. Starting with a very simple
algorithm allowed early experimentation with sensor and device configurations. Building iteratively upon a simple 
algorithm rather than attempting to use a complex machine learning algorithm or library immediately allows early 
identification of the challenges that are involved in machine learning. Iterative development also ensures that 
a basic working algorithm is available if unforeseen difficulties are found in implementing a more complex solution.

#### Strategy Version 1 {-}

##### Description {-}

The first version of the learning strategy considers the list of device and sensor events for a 
single training session. The simple algorithm proceeds as follows:

1. Find the last user action taken during the training session.
2. Perform that action whenever any event occurs.

Whenever the user completes a training session, the strategy is rebuilt based on the session.

Implementing this simple strategy allowed for development of several building blocks for the 
machine learning component:

- An entity that observes incoming events and feeds them to the learning strategy.
- An entity that retrieves events from a training session and builds a strategy using the events

The machine learning component makes use of a Strategy Pattern, which allows different 
implementations of the learning strategy to be interchanged easily.

##### Outcome {-}

This strategy performs very poorly. Actions are triggered by random reports from 
sensors; the algorithm is unable to learn to perform any useful task.

#### Strategy Version 2 {-}

##### Description {-}

The second strategy improved on the previous strategy by associating each user action in a training
session with the event that immediately preceded it. This allows the system to learn to perform
multiple actions.

##### Outcome {-}

Using this strategy, the learning component is occasionally able to learn the desired action. 
However, this strategy results in a very high false positive rate; the algorithm frequently performs
user actions in response to events that are not intended to trigger the action.

#### Strategy Version 3 {-}

##### Description {-}

In addition to looking at all user actions in a training session,  the third strategy uses the 
state of all sensors at the beginning of a training session to filter out events that did not 
actually cause a change in the state of the home environment. This strategy triggers a user action 
based on the first event that indicated a change in the state of the system.

##### Outcome {-}

Using this strategy, the system is able to learn the correct action to take in a given scenario.
However, it was found that the system often associates user actions with small variations in 
sensor values, such as temperatures. The effect is that the system often takes action at
inappropriate times, due to the misidentification of small fluctuations as trigger events.

#### Strategy Version 4 {-}

##### Description {-}

The fourth and final strategy builds on version three by using data from multiple training sessions
in order to ignore noise in the training data. This strategy can make use of *negative* training
sessions. A negative training session is a session in which the user does not perform the 
action that they are attempting to train the system. Negative training sessions allow this strategy
to filter out training data that is not strongly associated with a user action that was taken during
a positive training session. 

The algorithm counts the number of times an event was seen across all training sessions
and comparing this value to the number of times the event was also associated with a particular
user action. The ratio of `(total event count) / (association count)` is compared to a threshold
parameter. Only events with a ratio above the threshold trigger an action from the learning component.
The following pseudocode describes the algorithm.

```c
eventCounts = {}          // Tracks the total number of times that an event was seen across all training sessions
DECISION_THRESHOLD = 0.8  // Weight parameter - the threshold for triggering an action 
LOOKBACK_WINDOW = 5       // Number of events to consider associating with an action

// Interface for providing data from a new training session
void processTrainingSession(event[] events)
{
    global eventCounts

    for (i = 0 to events.length)
    {
        event = events[i]
        eventCounts[event]++ //Increment the number of times this event has been encountered
        if (isUserAction(event))
        {
            action = event
            for ( j = (i - LOOKBACK_WINDOW) to i) 
            {
                e = events[j]
                incrementAssociationCount(e, action)
            }
        }
    }
}

// Interface for determining which actions to take in response to an event
decision[] findDecisionsForEvent(e) 
{
    decisions = []
    associations = getAssociationsForEvent(e)
    for (a in associations)
    {
        // If the ratio of (number of times associated with the event)/(number of times event was seen)
        // is greater than the threshold value, add the action to the list of decisions returned
        if ( (a.count / eventCounts[e]) > DECISION_THRESHOLD)
        {
            decisions.append(a.action)
        }
    }
    return decisions
}
```
