import uuid
import gradio as gr
from abc import ABC, abstractmethod
from typing import List, Any, Callable, Union, Optional

class SignalEmitter(ABC):
    """
    Abstract Base Class for UI components that emit data to an orchestrator.
    
    This class implements the 'Outbox Pattern' for Gradio. It decouples internal 
    component events (e.g., button clicks) from the orchestrator's event handlers.
    """

    def __init__(self):
        """Initializes internal states for signal transmission."""
        self._outbox_payload = gr.State(value=None)
        self._outbox_trigger = gr.State(value="")

    def _send_on(
        self, 
        event_trigger: Any, 
        inputs: Optional[Union[gr.Component, List[gr.Component]]],
        fn_process: Optional[Callable] = None
    ) -> None:
        """
        Wires an internal Gradio component event to the signal emission logic.
        
        Subclasses should call this during initialization to define which UI actions 
        trigger a signal to the outside world.
        
        Args:
            event_trigger: A Gradio event listener (e.g., self.submit_btn.click).
            inputs: Component(s) from which data will be harvested for the signal.
                    Pass None if the signal is triggered by an event without data (e.g. a simple button click).
            fn_process: Optional transformation function. Receives values from 
                        `inputs` and returns the final payload. If None, the 
                        first input value is used.
        Returns:
            Any: The Gradio event dependency object.
        """
        # Critical Fix: Gradio expects an empty list for no inputs, not [None].
        if inputs is None:
            inputs = []
        elif not isinstance(inputs, list): 
            inputs = [inputs]

        def _transmission_wrapper(*args):
            """Internal wrapper to package data with a unique identifier."""
            if fn_process:
                data = fn_process(*args)
            else:
                data = args[0] if args else None
            
            # Returning a new UUID ensures the .change() event fires in the orchestrator
            return (data, str(uuid.uuid4()))

        return event_trigger(
            fn=_transmission_wrapper,
            inputs=inputs,
            outputs=[self._outbox_payload, self._outbox_trigger]
        )

    def on_signal(self, fn: Callable, outputs: Optional[List[gr.Component]] = None) -> None:
        """
        Registers an external callback to handle emitted signals.
        
        This is the public API used by the orchestrator to 'subscribe' to the 
        component's data output.
        
        Args:
            fn: Callback function receiving the payload as its first argument.
            outputs: Optional list of Gradio components to be updated by the 
                     callback's return value.
        """
        if outputs is None: 
            outputs = []
            
        self._outbox_trigger.change(
            fn=fn, 
            inputs=[self._outbox_payload], 
            outputs=outputs
        )


class SignalReceiver(ABC):
    """
    Abstract Base Class for UI components that receive data from an orchestrator.
    
    This class implements the 'Inbox Pattern' for Gradio. It solves the issue 
    of redundant data (where Gradio skips updates if state remains identical) 
    by wrapping incoming data with a unique execution ID.
    
    Attributes:
        _inbox_payload (gr.State): Internal Gradio state holding the received data.
        _inbox_trigger (gr.State): Internal UUID state that forces the internal 
                                   `update` logic to run on every reception.
    """

    def __init__(self, targets: List[gr.Component]):
        """
        Initializes the receiver and binds the internal update pipeline.
        
        Args:
            targets: List of UI components managed by this receiver. The return 
                     value of the `update` method will be mapped to these.
        """
        self._inbox_payload = gr.State(value=None)
        self._inbox_trigger = gr.State(value="")
        
        # Internal reactive link: 
        # Any change in the trigger forces the execution of the update method.
        self._inbox_trigger.change(
            fn=self.update,
            inputs=[self._inbox_payload],
            outputs=targets
        )

    @abstractmethod
    def update(self, data: Any) -> Any:
        """
        Transforms incoming domain data into visual UI updates.
        
        Abstract method to be implemented by subclasses. This is where 
        presentation logic (formatting, color changes, visibility) resides.
        
        Args:
            data: Raw data payload received from the orchestrator.
            
        Returns:
            The update payload(s) for the components defined in `targets`.
        """
        pass

    def receive_from(
        self, 
        trigger_event: Any, 
        fn_fetch: Callable, 
        inputs: Optional[List[gr.Component]] = None
    ) -> None:
        """
        Connects an external trigger and data provider to this receiver's inbox.
        
        This is the public API used by the orchestrator to feed data into the 
        component from an external source (like a State Buffer or Timer).
        
        Args:
            trigger_event: The Gradio event initiating the fetch (e.g., timer.tick).
            fn_fetch: Provider function that returns the data to be received.
            inputs: Optional list of components required by `fn_fetch`.
        """
        if inputs is None: 
            inputs = []

        def _reception_wrapper(*args):
            """Internal wrapper to fetch data and generate a sync UUID."""
            data = fn_fetch(*args)
            return (data, str(uuid.uuid4()))
            
        trigger_event.then(
            fn=_reception_wrapper, 
            inputs=inputs, 
            outputs=[self._inbox_payload, self._inbox_trigger]
        )